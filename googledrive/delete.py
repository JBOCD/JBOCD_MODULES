# Include the Google Drive SDK
import os
import sys
import simplejson
import string
import ConfigParser
import httplib2
import json
from urllib import urlencode
from oauth2client.client import AccessTokenCredentials
from apiclient.discovery import build
from apiclient import errors

def PrintHelp():
    print "Python Google Drive Deleter"
    print "usage: python delete.py [access token] [remote file path]"

if len(sys.argv) < 2 : print "Delete.py: Access token cannot be null. (Argument 1)"
elif len(sys.argv) < 3 : print "Delete.py: Please enter the file you want to delete. (Argument 2)"
else:
    def ConfigSectionMap(section):
        dict1 = {}
        options = Config.options(section)
        for option in options:
            try:
                dict1[option] = Config.get(section, option)
                if dict1[option] == -1:
                    DebugPrint("skip: %s" % option)
            except:
                print("exception on %s!" % option)
                dict1[option] = None
        return dict1

    # Get configuration file
    Config = ConfigParser.ConfigParser()
    Config.read("/var/JBOCD/module/googledrive/config.ini")
    CLIENT_ID = ConfigSectionMap("googledrive")['clientid']
    CLIENT_SECRET = ConfigSectionMap("googledrive")['clientsecret']
    REDIRECT_URI = "urn:ietf:wg:oauth:2.0:oob"
    SCOPES = ['https://www.googleapis.com/auth/drive']

    at = simplejson.loads(sys.argv[1])
    h = httplib2.Http()
    d = {"grant_type": "refresh_token", "client_secret": CLIENT_SECRET, "client_id": CLIENT_ID, "refresh_token": at['refresh_token']}
    resp, content = h.request("https://accounts.google.com/o/oauth2/token", "POST", body=urlencode(d), headers={'Content-type' : 'application/x-www-form-urlencoded'})
    
    credentials = AccessTokenCredentials(json.loads(content)['access_token'], 'python-jbocd/1.0')
    

    http = httplib2.Http()
    http = credentials.authorize(http)
    drive = build('drive', 'v2', http=http)

    root = drive.about().get().execute()['rootFolderId']
    str = sys.argv[2]
    cur = root
    strsplt = str[1:].split('/')
    filename = strsplt[len(strsplt)-1]

    if len(strsplt) > 1:
        for folder in strsplt:
            param = {}
            param['pageToken'] = cur
            childrens = drive.children().list(folderId=cur).execute()
            for item in childrens['items']:
                sitem = drive.files().get(fileId=item['id']).execute()
                if sitem["labels"]["trashed"] == False and sitem["mimeType"] == "application/vnd.google-apps.folder":
                    if sitem["title"]==folder:
                        cur = item['id']
                        break

        if drive.files().get(fileId=cur).execute()['title'] != strsplt[len(strsplt)-2]:
            print "Directory not found!"
            exit(2)

    childrens = drive.children().list(folderId=cur).execute()
    for item in childrens['items']:
        sitem = drive.files().get(fileId=item['id']).execute()
        if sitem['title'] == filename:
            drive.files().delete(fileId=sitem['id']).execute()
            sys.exit(0)
    
    sys.exit(1)
