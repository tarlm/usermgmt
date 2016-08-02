# -*- coding:utf-8 -*-
import csv


## buil a dictionary contains the nit ad user from csv
def build_ad_nit(csv_nit_path) : 
	local_ad_nit = {}
	fieldnames = ['id_gaia', 'nom', 'prenom', 'email']
	with open(csv_nit_path, 'rb') as nit_csv_file: 
		nit_reader = csv.DictReader(nit_csv_file, fieldnames=fieldnames, restval=None, dialect='excel')
		local_ad_nit = {row['id_gaia']:[row['id_gaia'], row['nom'], row['prenom'], row['email']] for row in  nit_reader}

	print str(local_ad_nit['VV5193'])

	return local_ad_nit


## buil a dictionary contains the gaia ad user from csv
def build_ad_gaia(csv_gaia_path) : 	
	local_ad_gaia = {}
	fieldnames = ['id_gaia', 'nom', 'prenom', 'email']
	with open(csv_nit_path, 'rb') as gaia_csv_file: 
		gaia_reader = csv.DictReader(gaia_csv_file, fieldnames=fieldnames, restval=None, dialect='excel')

		for row in spamreader:
			print ', '.join(row)
			local_ad_gaia = None


	return local_ad_gaia




if __name__ == "__main__":

	ad_nit = {} # just to know the return object is dictionary
	ad_gaia = {} # just to know the return object is dictionary

	# build ad nit dictionary
	ad_nit =  build_ad_nit('ressources/Export_AD_04072016.csv') 

	# build ad gaia dictionary
	#ad_gaia = build_ad_gaia('ressources/20160701_074608_TB5_GAIA_2016_0630.csv') 

	## process the dictionary
	if not ad_nit:
		print "The Nit csv file can not be handled"

	if not ad_nit:
		print "The GAIA csv file can not be handled"
	
	if(ad_nit & ad_gaia):
		process(ad_nit, ad_gaia)