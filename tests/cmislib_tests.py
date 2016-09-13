#!/usr/bin/env python
# Alfresco extension to CMIS
import cmislibalf

from cmislib import CmisClient, Repository, Folder
from cmislib.model import CmisId
from cmislib.exceptions import CmisException, UpdateConflictException
import os, sys

try:
    # client = CmisClient('https://cmis.alfresco.com/api/-default-/public/cmis/versions/1.0/atom', 'admin', 'password')
    cmisClient = CmisClient('https://cmis.alfresco.com/api/-default-/public/cmis/versions/1.1/atom', 'admin', 'admin')
    repo = cmisClient.defaultRepository

except CmisException as cme:
    print "failed to connect to Alfresco: \r\n%s" % cme
    quit()

try:
    print 'Getting list of sites ..'
    folders = repo.query("select * from cmis:folder where cmis:objectTypeId='F:st:site'")
    print 'Processing list ..'
    for folder in folders:
        obj = repo.getObject(folder.id)
        # properties items are key-value TUPLES ..
        for key,val in obj.properties.items():
            if key=='cm:name' or key=='cm:title' or key=='cmis:path':
                print key,'=',val

except ValueError as vle:
    print "failed to read site list: \r\n%s" % vle