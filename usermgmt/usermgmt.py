# -*- coding:utf-8 -*-
import csv
from sys import exit


# this User object will be used in optimisation ==> second stepp
class User(object):
    def __init__(self):
        self.id_gaia = "anonyme"
        self.nom = "anonyme"
        self.prenom = "anonyme"
        self.email = "anonyme@example.com"
        self.status = "active"

    # return TRUE if both users attributs are equals and false if not
    def equal(self, user):
        return (self.id_gaia.upper()==user.id_gaia.upper()) & (self.nom.upper()==user.nom.upper()) & (self.prenom.upper()==user.prenom.upper()) & (self.email.upper()==user.email.upper())


# Description: build a dictionary contains the nit ad user from csv
# Key: the gaia id of the user
# Value: a list contains in order, id_gaia, nom, prenom, email
def build_ad_nit(csv_nit_path, fieldnames):
    # local_ad_nit = {}
    with open(csv_nit_path, 'rb') as nit_csv_file:
        nit_reader = csv.DictReader(nit_csv_file, fieldnames=fieldnames, delimiter=';', dialect='excel')
        next(nit_reader)  # skip header row
        local_ad_nit = {row[fieldnames[0]]: [row[fieldnames[0]], row[fieldnames[1]], row[fieldnames[2]]] for row in
                        nit_reader}

    return local_ad_nit


# Description: build a dictionary contains the gaia ad user from csv
# Key: the gaia id of the user
# Value: a list contains in order, id_gaia, nom, prenom, email
def build_ad_gaia(csv_gaia_path, fieldnames, dr_elec):
    user_dr_elec_nbre = 0
    local_ad_gaia = {}

    with open(csv_gaia_path, 'rb') as gaia_csv_file:
        gaia_reader = csv.DictReader(gaia_csv_file, fieldnames=fieldnames, delimiter=';', dialect='excel')
        next(gaia_reader)  # skip header row

        # optimisation in order to remove user belongs to DR elec
        for row in gaia_reader:
            # skip users belong to the elec's DR
            user_dr = row['code_orga']
            if user_dr[:4] in dr_elec:
                print 'Info: Skiping the user %s %s %s %s with DR %s belongs to DR ELEC.' % (
                    row['id_gaia'], row['prenom'], row['nom'], row['email'], row['code_orga'])
                user_dr_elec_nbre += 1
                continue

            local_ad_gaia[row['id_gaia']] = [row['id_gaia'], row['prenom'], row['nom'], row['email']]

    print 'There are %s users from DR ELEC' % user_dr_elec_nbre

    return local_ad_gaia


def process(ad_nit, ad_gaia):
    pass


if __name__ == "__main__":

    ad_nit = {}  # just to know the return object is dictionary
    ad_gaia = {}  # just to know the return object is dictionary

    nitFieldnames = ['id_gaia', 'nom', 'email']
    gaiaFieldnames = ['id_gaia', 'id_rh', 'prenom', 'nom', 'status_gaia', 'email', 'code_orga', 'working_site',
                      'user_type']
    dr_elec = ['1306', '1307', '1308', '1334', '1335', '1336', '1364', '1365', '1366',
               '1395', '1396', '1397', '1424', '1425', '1429', '1444', '1445', '1449', '1450', '1464', '1465', '1466',
               '1494', '1496', '1497']

    # build ad nit dictionary
    ad_nit_csv = '../resources/Export_AD_04072016.csv'
    ad_nit = build_ad_nit(ad_nit_csv, fieldnames=nitFieldnames)
    print "la taille de l'AD NIT est %s" % len(ad_nit)
    print "l'utilisateur d'id gaia: %s, de nom: %s et d'email: %s" % (
        ad_nit['VV5193'][0], ad_nit['VV5193'][1], ad_nit['VV5193'][2])

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
        process(ad_nit, ad_gaia)
