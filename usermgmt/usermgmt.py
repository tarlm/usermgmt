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

    def equal(self, user):
        pass




# Description: buil a dictionary contains the nit ad user from csv
# Key: the gaia id of the user
# Value: a list contains in order, id_gaia, nom, prenom, email
def build_ad_nit(csv_nit_path, fieldnames):
    # local_ad_nit = {}
    with open(csv_nit_path, 'rb') as nit_csv_file:
        nit_reader = csv.DictReader(nit_csv_file, fieldnames=fieldnames, delimiter=';', dialect='excel')
        local_ad_nit = {row[fieldnames[0]]: [row[fieldnames[0]], row[fieldnames[1]], row[fieldnames[2]]] for row in
                        nit_reader}
    return local_ad_nit


# Description: buil a dictionary contains the gaia ad user from csv
# Key: the gaia id of the user
# Value: a list contains in order, id_gaia, nom, prenom, email
def build_ad_gaia(csv_gaia_path, fieldnames):
    # local_ad_gaia = {}
    with open(csv_gaia_path, 'rb') as gaia_csv_file:
        gaia_reader = csv.DictReader(gaia_csv_file, fieldnames=fieldnames, delimiter=';', dialect='excel')

        local_ad_gaia = {row[fieldnames[0]]: [row[fieldnames[0]], row[fieldnames[1]], row[fieldnames[2]],
                                              row[fieldnames[3]]] for row in gaia_reader}
    return local_ad_gaia


def process(ad_nit, ad_gaia):
    pass


if __name__ == "__main__":

    ad_nit = {}  # just to know the return object is dictionary
    ad_gaia = {}  # just to know the return object is dictionary

    nitFieldnames = ['id_gaia', 'nom', 'email']
    gaiaFieldnames = ['id_gaia', 'nom', 'prenom', 'email']

    # build ad nit dictionary
    ad_nit = build_ad_nit('../resources/Export_AD_04072016.csv', fieldnames=nitFieldnames)
    print len(ad_nit)

    # build ad gaia dictionary
    ad_gaia = build_ad_gaia('../resources/20160701_074608_TB5_GAIA_2016_0630.csv', fieldnames=gaiaFieldnames)
    print len(ad_gaia)

    # process the dictionary
    if not ad_nit:
        print "The Nit csv file can not be handled"
        exit(1)

    if not ad_gaia:
        print "The GAIA csv file can not be handled"
        exit(1)

        # if ad_nit & ad_gaia:
        #    process(ad_nit, ad_gaia)
