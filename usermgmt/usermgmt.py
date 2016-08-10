# -*- coding:utf-8 -*-
import csv, re, inspect, logging, codecs, cStringIO

from sys import exit


############ Known python tooltip classes for handling unicode #####

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


class UnicodeReader:
    """
    A CSV reader which will iterate over lines in the CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwds)

    def next(self):
        row = self.reader.next()
        return [unicode(s, "utf-8") for s in row]

    def __iter__(self):
        return self


class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])
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


############ EOF: Known python tooltip classes for handling unicode #####


EMAIL_REGEX = re.compile("^[A-Za-z].*@.*((grdf|erdf-grdf)\.fr)$")  # use http://pythex.org/ to validate the regex first


class User(object):
    """
    This User object is used to hold a user identity. This model is easy for data manipulation
    """

    def __init__(self, id_gaia="anonyme", nom="anonyme", prenom="anonyme", email="anonyme@example.com",
                 status="inactive"):
        """
        :param id_gaia: the gaia id of the corresponding user
        :param nom: the family name of the current user
        :param prenom: the firstname of the current user
        :param email:
        :param status:
        :return:
        """
        self.id_gaia = id_gaia
        self.nom = nom
        self.prenom = prenom
        self.email = email
        self.status = status

    def __str__(self):
        return "I'm %s with GAIA: %s, and email: %s" % (self.prenom + " " + self.nom, self.id_gaia, self.email)

    def is_same_gaia(self, user):

        #  check if current user has same gaia as the user in parameter
        return self.id_gaia.upper() == user.id_gaia.upper()

    def is_active(self):
        """ check if current user is active
        :return: True if user is active and False if not
        """
        if self.status in ('Activé', 'A initialiser', 'active', 'Verrouillé'):
            return True
        else:
            return False

    def equal(self, user):
        """ Compare current user to another from param
        :param user: user to compare the current user with
        :return: TRUE if both users attributs are equals and false if not
        """
        return (self.id_gaia.upper() == user.id_gaia.upper()) & (self.nom.upper() == user.nom.upper()) & (
            self.prenom.upper() == user.prenom.upper()) & (self.email.upper() == user.email.upper())

    def normalize(self):
        """ function use to normalize user if wanted
        :return: None
        """
        # normalize nom
        if self.nom:
            self.nom = self.nom.upper()
        else:
            self.nom = "ANONYME"

        # normalize prenom
        if self.prenom:
            self.prenom = self.prenom.capitalize()
        else:
            self.prenom = "ANONYME"

        # normalize email
        if not self.email:
            self.email = "anonyme@example.com"

        # normalize status
        if not self.status:
            self.email = "inactive"


# TODO: load the config file from conf folder and build config object
def build_conf_file():
    """ build the conf object from config_file
    :return:
    """
    return NotImplemented


def build_ad_nit(csv_nit_path, fieldnames):
    """ build a dictionary contains the nit ad user from csv
    :param csv_nit_path:
    :param fieldnames:
    :return: a dictionary contains as key the gaia id of the user and as value the user object
    """
    local_ad_nit = {}
    with open(csv_nit_path, 'rb') as nit_csv_file:
        nit_reader = csv.DictReader(nit_csv_file, fieldnames=fieldnames, delimiter=';', dialect='excel')
        try:
            next(nit_reader)  # skip header row
            for row in nit_reader:
                # skip users without GAIA
                if not row['id_gaia']:
                    continue

                l_id_gaia = row['id_gaia'].strip() if row['id_gaia'] else row['id_gaia']
                l_nom = row['nom'].strip() if row['nom'] else row['nom']
                l_prenom = row['prenom'].strip() if row['prenom'] else row['prenom']
                l_email = row['email'].strip() if row['email'] else row['email']
                l_status = "active"
                local_ad_nit[l_id_gaia] = User(id_gaia=l_id_gaia, nom=l_nom, prenom=l_prenom, email=l_email,
                                               status=l_status)
        except csv.Error as cre:
            exit('file %s, line %d: %s' % (csv_nit_path, nit_reader.line_num, cre))

    return local_ad_nit


def build_ad_gaia(csv_gaia_path, fieldnames, dr_elec):
    """ build a dictionary contains the gaia ad user from csv
    :param csv_gaia_path: the path to gaia csv file
    :param fieldnames: a list contains in order, id_gaia, nom, prenom, email
    :param dr_elec:
    :return: a dictionary contains as key the gaia id of the user and as value the user object
    """
    user_dr_elec_nbre = 0
    local_ad_gaia = {}

    with open(csv_gaia_path, 'rb') as gaia_csv_file:
        gaia_reader = csv.DictReader(gaia_csv_file, fieldnames=fieldnames, delimiter=';', dialect='excel')
        try:
            next(gaia_reader)  # skip header row

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
                l_status = row['status_gaia'].strip() if row['status_gaia'] else "inactive"

                local_ad_gaia[l_id_gaia] = User(id_gaia=l_id_gaia, prenom=l_prenom, nom=l_nom, email=l_email,
                                                status=l_status)

        except csv.Error as cre:
            exit('file %s, line %d: %s' % (csv_gaia_path, gaia_reader.line_num, cre))

    print 'There are %s users from DR ELEC' % user_dr_elec_nbre

    return local_ad_gaia

def createCsvFile(userList, outputFileName):
    """ Method use to create csv files
    :param userList: a list of user's object for creation, deletion and update
    :param outputFileName: the file in which write users
    :return: None
    """
    with open(outputFileName, 'wb') as csv_file_out:
        writer = csv.writer(csv_file_out)
        try:
            print 'working'


        except csv.Error as cwe:
            print 'Can not write the file %s, line %d: %s' % (outputFileName, writer.line_num, cwe)


def build_user_to_be_deleted(ad_nit, ad_gaia):
    """ Build User to be remove from application source AD base on the following criteria
    1- User existe dans AD NIT et pas dans AD GAIA and not exist in exception list==> To be deleted
    2- User existe dans AD NIT et dans AD GAIA avec statut gaia "Désactivé" ou "N/A" ==> To be deleted
    :param ad_nit:
    :param ad_gaia:
    :return:
    """
    local_user_for_deletion = []
    for user_gaia_id, nitUserObject in ad_nit.items():
        # if the user not exist in AD GAIA, delete the user access
        if user_gaia_id not in ad_gaia:
            print "User %s does not exit in AD GAIA anymore. Going to remove the user" % user_gaia_id
            local_user_for_deletion.append(nitUserObject)
            continue

        gaia_user_object = ad_gaia.get(user_gaia_id)
        gaia_user_object.normalize()

        if not gaia_user_object.is_active():
            print "User %s is deactivated in AD GAIA anymore. Going to remove the user \t status= %s" % (
                user_gaia_id, gaia_user_object.status)
            local_user_for_deletion.append(gaia_user_object)

    return local_user_for_deletion


def build_user_to_be_updated(ad_nit, ad_gaia):
    pass


def build_user_to_be_created(ad_nit, ad_gaia):
    pass


if __name__ == "__main__":
    """ The main program """

    ad_nit = {}  # just to know the return object is dictionary
    ad_gaia = {}  # just to know the return object is dictionary
    user_for_update = []
    user_for_creation = []
    user_for_deletion = []

    configFile = build_conf_file()

    nitFieldnames = ['id_gaia', 'nom', 'prenom', 'email']
    gaiaFieldnames = ['id_gaia', 'id_rh', 'prenom', 'nom', 'status_gaia', 'email', 'code_orga', 'working_site',
                      'user_type']
    dr_elec = ['1306', '1307', '1308', '1334', '1335', '1336', '1364', '1365', '1366',
               '1395', '1396', '1397', '1424', '1425', '1429', '1444', '1445', '1449', '1450', '1464', '1465', '1466',
               '1494', '1496', '1497']

    # build ad nit dictionary
    ad_nit_csv = '../resources/Export_AD_04072016.csv'
    ad_nit = build_ad_nit(ad_nit_csv, fieldnames=nitFieldnames)
    print "la taille de l'AD NIT est %s" % len(ad_nit)

    # build ad gaia dictionary
    ad_gaia_csv = '../resources/20160701_074608_TB5_GAIA_2016_0630.csv'
    ad_gaia = build_ad_gaia(ad_gaia_csv, fieldnames=gaiaFieldnames, dr_elec=dr_elec)

    print "la taille de l'AD GAIA est %s" % len(ad_gaia)

    # process the dictionary
    if not ad_nit:
        print "The Nit csv file can not be handled"
        exit(1)

    if not ad_gaia:
        print "The GAIA csv file can not be handled"
        exit(1)

    if ad_nit and ad_gaia:
        user_for_deletion = build_user_to_be_deleted(ad_nit, ad_gaia)
        print "There is %s users to delete" % len(user_for_deletion)
        user_for_update = build_user_to_be_updated(ad_nit, ad_gaia)
        user_for_creation = build_user_to_be_created(ad_nit, ad_gaia)

    createCsvFile(userList=user_for_deletion, outputFileName="../resources/supprimerUser.csv")
