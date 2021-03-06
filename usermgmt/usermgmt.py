#!/usr/bin/python
#  -*- coding:utf-8 -*-
"""
Created on 6 juil. 2016
Support tool for users comparison and update AD NIT with changes coming from AD GAIA

@author: Rodrigue ADOUHOUEKONOU
"""
import cStringIO
import codecs
import csv
import re
import ConfigParser
import logging
from sys import exit

# use http://pythex.org/ to validate the regex first
mail_REGEX = re.compile("^[A-Za-z].*@.*((grdf|erdf-grdf)\.fr)$")
# 2 letters(case insensitive)+ 4 or more digits ==> Goal skip application service accounts
GAIA_REGEX = re.compile("^[A-Za-z]{2,}[0-9]{3,}$")


# GAIA_REGEX = re.compile("^[A-Za-z]{2}[0-9]{4}$")  # Strict 2 letters(case insensitive)+ 4 digits

class User(object):
    """
    This User object is used to hold a user identity. This model is easy for data manipulation
    """

    def __init__(self, idgaia=u'ANONYME', nom=u'ANONYME', prenom=u'Anonyme', mail=u'anonyme@example.com',
                 status=u'Inactivé'):
        """
        :param idgaia: the gaia id of the corresponding user
        :param nom: the family name of the current user
        :param prenom: the first name of the current user
        :param mail:
        :param status:
        :return:
        """
        self.idgaia = idgaia
        self.nom = nom
        self.prenom = prenom
        self.mail = mail
        self.status = status
        self.logger = logging.getLogger('usermgmt.User')
        self.logger.debug('Creating an instance of User: gaia=%s, firstname=%s, name=%s, mail=%s, status=%s' %
                          (self.idgaia, self.prenom, self.nom, self.mail, self.status))

    @staticmethod
    def string_equal_ignore_case(a, b):
        """
        Check if both strings get in param are equals despite the case
        :param a: first string
        :param b: string to compare
        :return: True if equal and false if not
        """
        try:
            return a.upper() == b.upper()
        except AttributeError:
            return False

    @staticmethod
    def string_equal_case_sensitive(a, b):
        """
        Check if both strings get in param are strict equals
        :param a: first string
        :param b: string to compare
        :return: True if equal and false if not
        """
        try:
            return a == b
        except AttributeError:
            return False

    def is_same_gaia(self, new_user):

        """
        check if current new_user has same gaia as the new_user in parameter
        :param new_user:
        :return:
        """
        return User.string_equal_ignore_case(self.idgaia, new_user.idgaia)

    def is_active(self):
        """ check if current user is active
        :return: True if user is active and False if not
        """
        if self.status in (u'Activé', u'A initialiser'):
            return True
        else:
            return False

    def is_external(self):
        """ check if current user is external
        :return: True if user is external and False if not
        """
        external_list = [u'external', u'externe']
        if any(x in self.mail for x in external_list):
            return True
        else:
            return False

    def equal(self, new_user):
        """ Compare current new_user to another from param
        :param new_user: new_user to compare the current new_user with
        :return: TRUE if both users attributes(gaia, nom, prenom, mail) are equals and false if not
        """
        return self.is_same_gaia(new_user=new_user) & User.string_equal_ignore_case(self.nom, new_user.nom) \
               & User.string_equal_ignore_case(self.prenom, new_user.prenom) \
               & User.string_equal_ignore_case(self.mail, new_user.mail)

    def normalize(self):
        """ function use to normalize user if wanted
        :return: None
        """
        # normalize nom
        try:
            self.nom = self.nom.upper()
        except AttributeError:
            self.nom = self.nom

        # normalize prenom
        try:
            self.prenom = self.prenom.capitalize()
        except AttributeError:
            self.prenom = self.prenom

    def is_mail_name_firstname_changed(self, new_user):
        """ check if current new_user's name or mail change to new new_user.
        :param new_user: the user with whom the comparison will be done
        :return: True if new_user is change and False if not
        """

        # User has different Name and mail from AD GAIA to AD NIT
        if (not User.string_equal_ignore_case(self.mail, new_user.mail) and
                not User.string_equal_case_sensitive(self.nom, new_user.nom)):
            self.logger.info(
                'User %s has different mail and Name property from ad_gaia to ad_nit. Update requested in AD NIT' %
                self.idgaia)
            return True

        # User has different mail from AD GAIA to AD NIT
        if not User.string_equal_ignore_case(self.mail, new_user.mail):
            self.logger.info(
                'User %s has different Email property from ad_gaia to ad_nit. Update requested in AD NIT' %
                self.idgaia)
            return True

        # User has different Name from AD GAIA to AD NIT
        if not User.string_equal_case_sensitive(self.nom, new_user.nom):
            self.logger.info(
                'User %s has different Name property from ad_gaia to ad_nit. Update requested in AD NIT' % self.idgaia)
            return True

        # User has different firstname from AD GAIA to AD NIT
        if not User.string_equal_case_sensitive(self.prenom, new_user.prenom):
            self.logger.info(
                'User %s has different prenom property from ad_gaia to ad_nit. Update requested in AD NIT' %
                self.idgaia)
            return True

        return False

    def __str__(self):
        return "I'm %s %s with GAIA: %s, mail: %s and Status: %s" % (
            self.prenom, self.nom, self.idgaia, self.mail, self.status)


class UTF8Recoder:
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8
    """

    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode("utf-8")


class UnicodeDictReader:
    """
    A CSV reader which will iterate over lines in the CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwds)
        self.header = self.reader.next()

    def next(self):
        row = self.reader.next()
        vals = [unicode(s, "utf-8") for s in row]
        return dict((self.header[x], vals[x]) for x in range(len(self.header)))

    def __iter__(self):
        return self


class UnicodeDictWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, fieldnames, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.fieldnames = fieldnames
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writeheader(self):
        self.writer.writerow(self.fieldnames)

    def writerow(self, row):
        self.writer.writerow([row[x].encode("utf-8") for x in self.fieldnames])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


def extract_as_list(str_param):
    """ Split a string in list by comma then filter empty character
    :param str_param: the string to split
    :return: the list
    """
    str_list = str_param.split(',')
    str_list = filter(None, [x.strip() for x in str_list])

    return str_list


def build_conf_file():
    """ build the conf object from config_file
    :return:
    """
    logging.debug('### Started: building configuration file ###')

    l_config_object = {}

    l_config_file = ConfigParser.ConfigParser()
    config_filenames = "conf/user_config.cfg"

    logging.debug('read the configuration parameters from: ' + config_filenames)

    l_config_file.read(filenames=config_filenames)

    # get list of dr elec as string then split by comma and strip 'space' in case they are.
    l_config_object['dr_elec_list'] = extract_as_list(l_config_file.get('DRELEC', 'drList'))

    # get list of csv fields
    l_config_object['csvFieldnames'] = extract_as_list(l_config_file.get('CSV_IN', 'csvFieldnames'))

    l_config_object['ad_nit_csv'] = l_config_file.get('CSV_IN', 'ad_nit_csv')

    l_config_object['csv_delimiter'] = l_config_file.get('CSV_IN', 'csv_delimiter')

    l_config_object['csv_encoding'] = l_config_file.get('CSV_IN', 'csv_encoding')

    l_config_object['ad_gaia_csv'] = l_config_file.get('CSV_IN', 'ad_gaia_csv')

    l_config_object['users_except_csv'] = l_config_file.get('CSV_IN', 'users_except_csv')

    l_config_object['user_creation_csv'] = l_config_file.get('CSV_OUT', 'user_creation_csv')

    l_config_object['user_deletion_csv'] = l_config_file.get('CSV_OUT', 'user_deletion_csv')

    l_config_object['user_update_csv'] = l_config_file.get('CSV_OUT', 'user_update_csv')

    logging.debug('### Ended: building configuration file ###')

    return l_config_object


def build_ad_nit(csv_path, encoding="utf-8", delimiter=';'):
    """ build a dictionary contains the nit ad user from csv
    :param csv_path:
    :param encoding:
    :param delimiter:
    :return: a dictionary contains as key the gaia id of the user and as value the user object
    """

    logging.debug('Load user dictionary from %s csv file' % csv_path)

    local_ad_nit = {}
    with open(csv_path, 'rb') as nit_csv_file:

        nit_reader = UnicodeDictReader(nit_csv_file, dialect=csv.excel, encoding=encoding,
                                       delimiter=delimiter, skipinitialspace=True)

        try:

            for row in nit_reader:
                # skip users without GAIA
                if not row['IDGAIA']:
                    logging.info('Skip user from AD NIT file. Reason: No ID GAIA')
                    continue

                l_idgaia = row['IDGAIA'].strip() if row['IDGAIA'] else row['IDGAIA']
                l_nom = row['NOM'].strip() if row['NOM'] else row['NOM']
                l_prenom = row['PRENOM'].strip() if row['PRENOM'] else row['PRENOM']
                l_mail = row['MAIL'].strip() if row['MAIL'] else row['MAIL']
                l_status = u'Activé'
                local_ad_nit[l_idgaia] = User(idgaia=l_idgaia, nom=l_nom, prenom=l_prenom, mail=l_mail,
                                               status=l_status)
        except csv.Error as cre:
            logging.error('exception raised in build_ad_nit, file %s, line %d: %s' % (
                csv_path, nit_reader.reader.line_num, cre))
            exit('file %s, line %d: %s' % (csv_path, nit_reader.reader.line_num, cre))

    return local_ad_nit


def build_ad_gaia(csv_path, dr_elec, encoding="utf-8", delimiter=';'):
    """ build a dictionary contains the gaia ad user from csv
    :param csv_path: the path to gaia csv file
    :param dr_elec:
    :param encoding:
    :param delimiter:

    :return: a dictionary contains as key the gaia id of the user and as value the user object
    """
    user_dr_elec_nbre = 0
    local_ad_gaia = {}

    with open(csv_path, 'rb') as gaia_csv_file:

        gaia_reader = UnicodeDictReader(gaia_csv_file, dialect=csv.excel, encoding=encoding,
                                        delimiter=delimiter, skipinitialspace=True)
        try:

            # optimisation in order to remove user belongs to DR elec
            for row in gaia_reader:
                # skip users without GAIA
                l_idgaia = row['IDGAIA']
                if not l_idgaia:
                    logging.debug(
                        'Skip user %s %s %s. Reason: No ID GAIA' % (row['PRENOM'], row['NOM'], row['MAIL']))
                    continue

                l_idgaia = l_idgaia.strip()

                # skip users with Application account
                if not GAIA_REGEX.match(l_idgaia):
                    logging.debug(
                        'Skip user %s %s %s. Reason: GAIA is for service' % (l_idgaia, row['PRENOM'], row['NOM']))
                    continue

                # skip users no code organisation
                user_dr = row['CODEORGA']
                if not user_dr:
                    logging.debug('Skip user %s %s %s %s. Reason: No Code Organization' % (
                        l_idgaia, row['PRENOM'], row['NOM'], row['MAIL']))
                    continue

                user_dr = row['CODEORGA'].strip()

                # skip users belong to the elec's DR
                if user_dr[:4] in dr_elec:
                    logging.debug('Skip user %s %s %s %s with DR %s. Reason: belongs to DR ELEC.' % (
                        l_idgaia, row['PRENOM'], row['NOM'], row['MAIL'], user_dr))
                    user_dr_elec_nbre += 1
                    continue

                l_status = row['Statut GAIA']

                # skip users with no statut
                if not l_status:
                    logging.debug('Skip user %s %s %s %s. Reason: No Statut value' % (
                        l_idgaia, row['PRENOM'], row['NOM'], row['MAIL']))
                    continue

                l_status = l_status.strip()

                # skip users with statut 'Désactivé' or 'Verrouillé'
                if l_status in (u'Désactivé', u'Verrouillé'):
                    logging.debug('Skip user %s %s %s %s Statut=%s. Reason: Statut' % (
                        l_idgaia, row['PRENOM'], row['NOM'], row['MAIL'], l_status))
                    continue

                # Build gaia if none criteria match
                l_nom = row['NOM'].strip() if row['NOM'] else row['NOM']
                l_prenom = row['PRENOM'].strip() if row['PRENOM'] else row['PRENOM']
                l_mail = row['MAIL'].strip() if row['MAIL'] else row['MAIL']

                local_ad_gaia[l_idgaia] = User(idgaia=l_idgaia, prenom=l_prenom, nom=l_nom, mail=l_mail,
                                                status=l_status)

        except csv.Error as cre:
            logging.error('Error in build gaia function, file %s, line %d: %s' % (
                csv_path, gaia_reader.reader.line_num, cre))
            exit('file %s, line %d: %s' % (csv_path, gaia_reader.reader.line_num, cre))

    logging.info('There are %s users from DR ELEC' % user_dr_elec_nbre)

    return local_ad_gaia


def create_csv_file(user_list, fieldsnames, output_filename, encoding="utf-8", delimiter=';'):
    """ Method use to create csv files
    :param user_list: a list of user's object for creation, deletion and update
    :param fieldsnames: the name of the output file
    :param output_filename: the file in which write users
    :param encoding: the encoding to be used for the output file
    :param delimiter: the separator to be used in the csv file.
    :return: None
    """
    with open(output_filename, 'wb') as csv_file_out:

        csv_writer = UnicodeDictWriter(csv_file_out, fieldnames=fieldsnames, delimiter=delimiter, dialect=csv.excel,
                                       encoding=encoding)

        try:
            csv_writer.writeheader()  # write the csv header

            for user in user_list:
                row_dict = dict((field, user.__getattribute__(field.lower())) for field in fieldsnames)
                csv_writer.writerow(row_dict)

        except csv.Error as cwe:
            logging.error('Error writing csv file %s, line %d: %s' % (output_filename, csv_writer.writer.line_num, cwe))

        except AttributeError as ae:
            logging.error('Error writing csv file, message: %s' % ae)


def build_user_to_be_deleted(ad_nit_dict, ad_gaia_dict, exception_users_dict):
    """ Build User to be remove from application source AD base on the following criteria
    1. User existe dans AD NIT et pas dans AD GAIA and not exist in exception list==> To be deleted
    :param ad_nit_dict:
    :param ad_gaia_dict:
    :param exception_users_dict:  exception user dictionary
    :return: a list of users to be deleted from the AD. Build a csv file from the list
    """
    logging.debug('### Started: building list of deletion users ###')

    local_user_for_deletion = []
    for nituser_gaia_id, nitUserObject in ad_nit_dict.items():

        # 1. User exists dans AD NIT et pas dans AD GAIA and not exist in exception list
        # ==> add to delete and go for next user
        # ==> Remove the user from ad_nit_dict object
        if nituser_gaia_id not in ad_gaia_dict and nituser_gaia_id not in exception_users_dict:
            logging.debug(
                '%s is neither in AD GAIA nor in Exception list. Going to remove the user' % nituser_gaia_id)
            local_user_for_deletion.append(nitUserObject)
            del ad_nit_dict[nituser_gaia_id]
            logging.debug('Delete the user %s from ad nit dictionary' % nituser_gaia_id)
            continue
    logging.debug('### Ended: building list of deletion users ###')

    return local_user_for_deletion


def build_user_to_be_updated(ad_nit_dict, ad_gaia_dict, exception_user_dict):
    """ Build User to be updated from AD GAIA to AD NIT based on the following criteria
    1. User exists dans AD NIT et dans AD GAIA mais avec nom ou mail different
    2. User exists dans AD NIT et dans User Exception mais avec nom ou mail different
    :param ad_nit_dict:
    :param ad_gaia_dict:
    :param exception_user_dict:  exception user dictionary
    :return user_for_update: a list of user objects
    """

    logging.debug('### Started: building list of Updated users ###')
    user_for_update = []

    for nit_user_gaia_id, nit_user_object in ad_nit_dict.items():

        # 1. User exists dans AD NIT et dans AD GAIA mais avec nom ou mail different
        if nit_user_gaia_id in ad_gaia_dict:

            gaia_user_object = ad_gaia_dict.get(nit_user_gaia_id)

            # User has different Name and mail from AD GAIA to AD NIT
            if nit_user_object.is_mail_name_firstname_changed(gaia_user_object):
                gaia_user_object.normalize()
                user_for_update.append(gaia_user_object)
                continue

        # 2. User exists dans AD NIT et dans User Exception mais avec nom ou mail different
        if nit_user_gaia_id in exception_user_dict:

            exception_user_object = exception_user_dict.get(nit_user_gaia_id)

            # User has different Name and mail from AD Exception to AD NIT
            if nit_user_object.is_mail_name_firstname_changed(exception_user_object):
                exception_user_object.normalize()
                user_for_update.append(exception_user_object)
                continue

    logging.debug('### Ended: building list of Updated users ###')
    return user_for_update


def build_user_to_be_created(ad_nit_dict, ad_gaia_dict, exception_user_dict):
    """ Build User to be created from application source AD base on the following criteria
   1- User existe dans AD GAIA et pas dans AD NIT  and not exist in exception list==> To be deleted
   2- User existe dans AD NIT et dans AD GAIA avec statut gaia "Désactivé" ou "N/A" ==> To be deleted
   :param ad_nit_dict:
   :param ad_gaia_dict:
   :param exception_user_dict:  exception user dictionary
   :return user_for_creation: a list of users to be created
   """
    user_for_creation = []
    for gaia_user_id, gaia_user_object in ad_gaia_dict.items():

        if gaia_user_id not in ad_nit_dict and mail_REGEX.match(gaia_user_object.mail) and \
                GAIA_REGEX.match(gaia_user_id):
            logging.debug(
                'User %s from GAIA does not exit in AD NIT. Is user external?' % gaia_user_id)

            if not gaia_user_object.is_external():
                logging.debug('User %s is not external. Will be created' % gaia_user_id)
                gaia_user_object.normalize()
                user_for_creation.append(gaia_user_object)
            else:
                logging.debug('Skipped user %s: is external.' % gaia_user_id)

            continue

    # User exists in Exception AD and not in AD Nit.
    for except_user_id, except_user_object in exception_user_dict.items():
        if except_user_id not in ad_nit_dict:
            logging.debug('User %s from Exception does not exit in AD NIT. Adding user' % except_user_id)
            except_user_object.normalize()
            user_for_creation.append(except_user_object)
            continue

    return user_for_creation


def main():
    """ The main program """
    print 'Started the User managment tool'
    ad_nit_dict = {}  # just to know the return object is dictionary
    ad_gaia_dict = {}  # just to know the return object is dictionary

    logging.basicConfig(filename='log/usermgmt.log', format='%(asctime)s - %(levelname)s - %(message)s',
                        filemode='w', level=logging.DEBUG)

    logging.info('######################## Started the user management tool ########################')

    config_object = build_conf_file()

    # build ad nit dictionary

    ad_nit_csv = config_object.get('ad_nit_csv')
    encoding = config_object.get('csv_encoding')
    delimiter = config_object.get('csv_delimiter')

    logging.info('### Started: building NIT AD dictionary representation ###')
    ad_nit_dict = build_ad_nit(csv_path=ad_nit_csv, encoding=encoding, delimiter=delimiter)
    logging.info('### Ended: building NIT AD dictionary representation ###')
    logging.info("la taille de l'AD NIT est %s" % len(ad_nit_dict))

    # build Exception user list
    users_except_csv = config_object.get('users_except_csv')

    logging.info('### Started: building exception users dictionary representation ###')
    users_except_dict = build_ad_nit(csv_path=users_except_csv, encoding=encoding, delimiter=delimiter)

    logging.info('Normalizing exception users in order to avoid case typo error')
    for user_id, exceptUserObject in users_except_dict.items():
        exceptUserObject.normalize()

    logging.info('### Ended: building exception users dictionary representation ###')

    logging.info("le nombre d'utilisateur en exception est %s" % len(users_except_dict))

    # build ad gaia dictionary
    ad_gaia_csv = config_object.get('ad_gaia_csv')

    logging.info('### Started: building AD GAIA users dictionary representation ###')

    ad_gaia_dict = build_ad_gaia(csv_path=ad_gaia_csv, dr_elec=config_object.get('dr_elec_list'), encoding=encoding,
                                 delimiter=delimiter)
    logging.info('### Ended: building AD GAIA users dictionary representation ###')
    logging.info("la taille de l'AD GAIA est %s" % len(ad_gaia_dict))

    # process the dictionaries
    if not ad_nit_dict:
        logging.info("The Nit csv file can not be handled")
        exit(1)

    if not ad_gaia_dict:
        logging.info("The GAIA csv file can not be handled")
        exit(1)

    if ad_nit_dict and ad_gaia_dict:
        logging.info("### Start building users to be deleted list ###")
        user_for_deletion = build_user_to_be_deleted(ad_nit_dict=ad_nit_dict, ad_gaia_dict=ad_gaia_dict,
                                                     exception_users_dict=users_except_dict)
        logging.info("\t###There is %s users to delete" % len(user_for_deletion))
        create_csv_file(user_list=user_for_deletion, output_filename=config_object.get('user_deletion_csv'),
                        fieldsnames=config_object.get('csvFieldnames'))
        logging.info("### End building users to be deleted list ###")

        user_for_update = build_user_to_be_updated(ad_nit_dict=ad_nit_dict, ad_gaia_dict=ad_gaia_dict,
                                                   exception_user_dict=users_except_dict)
        logging.info("\t###There is %s users to update" % len(user_for_update))
        create_csv_file(user_list=user_for_update, output_filename=config_object.get('user_update_csv'),
                        fieldsnames=config_object.get('csvFieldnames'))

        user_for_creation = build_user_to_be_created(ad_nit_dict=ad_nit_dict, ad_gaia_dict=ad_gaia_dict,
                                                     exception_user_dict=users_except_dict)
        logging.info("\t###There is %s users to create" % len(user_for_creation))
        create_csv_file(user_list=user_for_creation, output_filename=config_object.get('user_creation_csv'),
                        fieldsnames=config_object.get('csvFieldnames'))

        logging.info('######################## Finished the user management tool ########################')

        print '\t\t/!\/!\/!\ Ended the User management tool: please have a look on the log file /!\/!\/!\ '


if __name__ == "__main__":
    main()
