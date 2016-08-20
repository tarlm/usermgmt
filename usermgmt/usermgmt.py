#!/usr/bin/python
#  -*- coding:utf-8 -*-
import cStringIO
import codecs
import csv
import re
import ConfigParser
from sys import exit

# use http://pythex.org/ to validate the regex first
EMAIL_REGEX = re.compile("^[A-Za-z].*@.*((grdf|erdf-grdf)\.fr)$")

class User(object):
    """
    This User object is used to hold a user identity. This model is easy for data manipulation
    """

    def __init__(self, id_gaia=u'ANONYME', nom=u'ANONYME', prenom=u'Anonyme', email=u'anonyme@example.com',
                 status=u'Inactivé'):
        """
        :param id_gaia: the gaia id of the corresponding user
        :param nom: the family name of the current user
        :param prenom: the first name of the current user
        :param email:
        :param status:
        :return:
        """
        self.id_gaia = id_gaia
        self.nom = nom
        self.prenom = prenom
        self.email = email
        self.status = status

    @staticmethod
    def string_equal(a, b):
        try:
            return a.upper() == b.upper()
        except AttributeError:
            return a == b

    def is_same_gaia(self, user):

        #  check if current user has same gaia as the user in parameter
        return self.string_equal(self.id_gaia, user.id_gaia)

    def is_active(self):
        """ check if current user is active
        :return: True if user is active and False if not
        """
        if self.status in (u'Activé', u'A initialiser', u'Active', u'Verrouillé'):
            return True
        else:
            return False

    def equal(self, user):
        """ Compare current user to another from param
        :param user: user to compare the current user with
        :return: TRUE if both users attributes(gaia, nom, prenom, email) are equals and false if not
        """
        return self.string_equal(self.id_gaia, user.id_gaia) & self.string_equal(self.nom,
                                                                                 user.nom) & self.string_equal(
            self.prenom, user.prenom) & self.string_equal(self.email, user.email)

    def normalize(self):
        """ function use to normalize user if wanted
        :return: None
        """
        # normalize nom
        if self.nom:
            self.nom = self.nom.upper()
        else:
            self.nom = u'anonyme'.upper()

        # normalize prenom
        if self.prenom:
            self.prenom = self.prenom.capitalize()
        else:
            self.prenom = u'anonyme'.capitalize()

        # normalize email
        if not self.email:
            self.email = u'anonyme@example.com'

        # normalize status
        if self.status:
            self.status = self.status.capitalize()
        else:
            self.status = u'inactivé'.capitalize()

    def __str__(self):
        return "I'm %s %s with GAIA: %s, email: %s and Status: %s" % (
            self.prenom, self.nom, self.id_gaia, self.email, self.status)


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
    """ Split a string in list by comma then filter empty caracter
    :param str_param: the string to split
    :return: the list
    """
    str_list = str_param.split(',')
    str_list = filter(None, [x.strip() for x in str_list])

    return str_list


# TODO: load the config file from conf folder and build config object
def build_conf_file():
    """ build the conf object from config_file
    :return:
    """
    l_config_object= {}
    l_configFile = ConfigParser.ConfigParser()
    l_configFile.read(filenames="../conf/user_config.ini")

    # get list of dr elec as string then split by comma and strip 'space' in case they are.
    l_config_object['dr_elec_list'] = extract_as_list(l_configFile.get('DRELEC', 'drList'))

    # get list of csv fields
    l_config_object['csvFieldnames'] = extract_as_list(l_configFile.get('CSV_CONF', 'csvFieldnames'))



    return l_config_object

def build_ad_nit(csv_nit_path):
    """ build a dictionary contains the nit ad user from csv
    :param csv_nit_path:
    :return: a dictionary contains as key the gaia id of the user and as value the user object
    """
    local_ad_nit = {}
    with open(csv_nit_path, 'rb') as nit_csv_file:

        nit_reader = UnicodeDictReader(nit_csv_file, dialect=csv.excel, encoding="utf-8", delimiter=';',
                                       skipinitialspace=True)

        try:
            # next(nit_reader)  # skip header row
            for row in nit_reader:
                # skip users without GAIA
                if not row['id_gaia']:
                    continue

                l_id_gaia = row['id_gaia'].strip() if row['id_gaia'] else row['id_gaia']
                l_nom = row['nom'].strip() if row['nom'] else row['nom']
                l_prenom = row['prenom'].strip() if row['prenom'] else row['prenom']
                l_email = row['email'].strip() if row['email'] else row['email']
                l_status = u'Activé'
                local_ad_nit[l_id_gaia] = User(id_gaia=l_id_gaia, nom=l_nom, prenom=l_prenom, email=l_email,
                                               status=l_status)
        except csv.Error as cre:
            exit('file %s, line %d: %s' % (csv_nit_path, nit_reader.reader.line_num, cre))

    return local_ad_nit


def build_ad_gaia(csv_gaia_path, dr_elec):
    """ build a dictionary contains the gaia ad user from csv
    :param csv_gaia_path: the path to gaia csv file
    :param dr_elec:
    :return: a dictionary contains as key the gaia id of the user and as value the user object
    """
    user_dr_elec_nbre = 0
    local_ad_gaia = {}

    with open(csv_gaia_path, 'rb') as gaia_csv_file:
        gaia_reader = UnicodeDictReader(gaia_csv_file, dialect=csv.excel, encoding="utf-8", delimiter=';',
                                        skipinitialspace=True)
        try:

            # optimisation in order to remove user belongs to DR elec
            for row in gaia_reader:
                # skip users without GAIA
                if not row['id_gaia']:
                    continue

                # skip users belong to the elec's DR
                user_dr = row['code_orga'].strip()
                if user_dr[:4] in dr_elec:
                    print 'Info: Skiping the user %s %s %s %s with DR %s belongs to DR ELEC.' % (
                        row['id_gaia'], row['prenom'], row['nom'], row['email'], row['code_orga'])
                    user_dr_elec_nbre += 1
                    continue

                l_id_gaia = row['id_gaia'].strip() if row['id_gaia'] else row['id_gaia']
                l_nom = row['nom'].strip() if row['nom'] else row['nom']
                l_prenom = row['prenom'].strip() if row['prenom'] else row['prenom']
                l_email = row['email'].strip() if row['email'] else row['email']
                l_status = row['Statut GAIA'].strip() if row['Statut GAIA'] else unicode("Inactive", "utf-8")

                local_ad_gaia[l_id_gaia] = User(id_gaia=l_id_gaia, prenom=l_prenom, nom=l_nom, email=l_email,
                                                status=l_status)

        except csv.Error as cre:
            exit('file %s, line %d: %s' % (csv_gaia_path, gaia_reader.reader.line_num, cre))

    print 'There are %s users from DR ELEC' % user_dr_elec_nbre

    return local_ad_gaia


def create_csv_file(user_list, fieldsnames, output_filename):
    """ Method use to create csv files
    :param user_list: a list of user's object for creation, deletion and update
    :param fieldsnames:
    :param output_filename: the file in which write users
    :return: None
    """
    with open(output_filename, 'wb') as csv_file_out:

        csv_writer = UnicodeDictWriter(csv_file_out, fieldnames=fieldsnames, delimiter=';', dialect=csv.excel,
                                       encoding="utf-8")

        try:
            csv_writer.writeheader()  # write the csv header

            for user in user_list:
                # fieldnames = ['id_gaia', 'nom', 'prenom', 'email']
                # return dict((self.header[x], vals[x]) for x in range(len(self.header)))
                row_dict = dict((field, user.__getattribute__(field)) for field in fieldsnames)
                csv_writer.writerow(row_dict)

        except csv.Error as cwe:
            print 'Can not write the file %s, line %d: %s' % (output_filename, csv_writer.writer.line_num, cwe)


def build_user_to_be_deleted(ad_nit_dist, ad_gaia_dict, exception_users_dict):
    """ Build User to be remove from application source AD base on the following criteria
    1. User existe dans AD NIT et pas dans AD GAIA and not exist in exception list==> To be deleted
    2. User existe dans AD NIT et pas dans AD GAIA and not exist in exception list==> To be deleted
    3. User existe dans AD NIT et dans AD GAIA avec statut gaia "Désactivé" ou "N/A" ==> To be deleted
    :param ad_nit_dist:
    :param ad_gaia_dict:
    :param exception_users_dict:  exception user dictionary
    :return:
    """
    local_user_for_deletion = []
    for nituser_gaia_id, nitUserObject in ad_nit_dist.items():

        # 1. User existe dans AD NIT et pas dans AD GAIA and not exist in exception list ==> add to delete and go for next user
        if nituser_gaia_id not in ad_gaia_dict and nituser_gaia_id not in exception_users_dict:
            print "User %s does not exit in AD GAIA anymore. Going to remove the user" % nituser_gaia_id
            local_user_for_deletion.append(nitUserObject)
            continue

        # nit user exists in gaia ad. Go for rule 2. and 3.

        gaiauser_object = ad_gaia_dict.get(nituser_gaia_id)

        if isinstance(gaiauser_object, User):
            gaiauser_object.normalize()
        else:
            print nituser_gaia_id + " not instance of user"
            continue

        # 2- User exists dans AD NIT et dans AD GAIA avec statut gaia "Désactivé" ou "N/A" ==> To be deleted
        if not gaiauser_object.is_active():
            print "User %s is deactivated in AD GAIA. Going to remove the user \t status= %s" % (
                nituser_gaia_id, gaiauser_object.status)
            local_user_for_deletion.append(gaiauser_object)

    return local_user_for_deletion


# TODO: Complete the method for creating csv for AD user update
def build_user_to_be_updated(ad_nit_dict, ad_gaia_dict, exception_user_dict):
    """ Build User to be remove from application source AD base on the following criteria
    1- User existe dans AD NIT et pas dans AD GAIA and not exist in exception list==> To be deleted
    2- User existe dans AD NIT et dans AD GAIA avec statut gaia "Désactivé" ou "N/A" ==> To be deleted
    :param ad_nit_dict:
    :param ad_gaia_dict:
    :param exception_user_dict:  exception user dictionary
    :return:
    """

    return NotImplemented


# TODO: Complete the method for creating csv for AD user creation
def build_user_to_be_created(ad_nit_dict, ad_gaia_dict, exception_user_dict):
    """ Build User to be remove from application source AD base on the following criteria
   1- User existe dans AD NIT et pas dans AD GAIA and not exist in exception list==> To be deleted
   2- User existe dans AD NIT et dans AD GAIA avec statut gaia "Désactivé" ou "N/A" ==> To be deleted
   :param ad_nit_dict:
   :param ad_gaia_dict:
   :param exception_user_dict:  exception user dictionary
   :return:
   """

    return NotImplemented


if __name__ == "__main__":
    """ The main program """

    ad_nit = {}  # just to know the return object is dictionary
    ad_gaia = {}  # just to know the return object is dictionary
    users_except_dict = {}
    user_for_update = []
    user_for_creation = []
    user_for_deletion = []

    configFile = build_conf_file()

    # build ad nit dictionary

    ad_nit_csv = configFile.get('ad_nit_csv')

    ad_nit = build_ad_nit(ad_nit_csv)
    print "la taille de l'AD NIT est %s" % len(ad_nit)

    # build ad nit dictionary
    users_except_dict_csv = configFile.get('users_except_dict_csv')
    users_except_dict = build_ad_nit(users_except_dict_csv)
    print "le nombre d'utilisateur en exception est %s" % len(ad_nit)

    # build ad gaia dictionary
    ad_gaia_csv = configFile.get('ad_gaia_csv')
    ad_gaia = build_ad_gaia(ad_gaia_csv, dr_elec = configFile.get('dr_elec_list'))

    print "la taille de l'AD GAIA est %s" % len(ad_gaia)

    # process the dictionary
    if not ad_nit:
        print "The Nit csv file can not be handled"
        exit(1)

    if not ad_gaia:
        print "The GAIA csv file can not be handled"
        exit(1)

    if ad_nit and ad_gaia:
        user_for_deletion = build_user_to_be_deleted(ad_nit, ad_gaia, users_except_dict)
        print "There is %s users to delete" % len(user_for_deletion)
        create_csv_file(user_list=user_for_deletion, output_filename="../resources/supprimerUser.csv",
                        fieldsnames=configFile.get('csvFieldnames'))

        user_for_update = build_user_to_be_updated(ad_nit_dict=ad_nit, ad_gaia_dict=ad_gaia,
                                                   exception_user_dict=users_except_dict)

        user_for_creation = build_user_to_be_created(ad_nit_dict=ad_nit, ad_gaia_dict=ad_gaia,
                                                     exception_user_dict=users_except_dict)
