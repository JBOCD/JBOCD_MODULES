# Include the Google Drive SDK
import os
import sys
import simplejson
import string
import ConfigParser
import httplib2
import json
import oauth2client.client
from urllib import urlencode
from oauth2client.client import AccessTokenCredentials
from apiclient.discovery import build
from apiclient import errors

def PrintHelp():
    print "Python Google Drive Deleter"
    print "usage: python put.py [access token] [remote file path] [local file path]"

if len(sys.argv) < 2 : print "put.py: Access token cannot be null. (Argument 1)"
elif len(sys.argv) < 3 : print "put.py: Please enter the remote file path (Argument 2)"
elif len(sys.argv) < 4 : print "put.py: Please enter the local file path. (Argument 3)"
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

    #at = simplejson.loads(sys.argv[1])
    #h = httplib2.Http()
    #d = {"grant_type": "refresh_token", "client_secret": CLIENT_SECRET, "client_id": CLIENT_ID, "refresh_token": at['refresh_token']}
    #resp, content = h.request("https://accounts.google.com/o/oauth2/token", "POST", body=urlencode(d), headers={'Content-type' : 'application/x-www-form-urlencoded'})
    
    #credentials = AccessTokenCredentials(json.loads(content)['access_token'], 'python-jbocd/1.0')
    

    #http = httplib2.Http()
    #http = credentials.authorize(http)
    #drive = build('drive', 'v2', http=http)

    credstr = '{"_module": "oauth2client.client", "token_expiry": null, "access_token": null, "token_uri": null, "invalid": false, "token_response": null, "client_id": "%s", "id_token": null, "client_secret": "%s", "revoke_uri": null, "_class": "AccessTokenCredentials", "refresh_token": "%s", "user_agent": "python-jbocd/1.0"}' % (  CLIENT_ID, CLIENT_SECRET, at['refresh_token'])
    credentials = AccessTokenCredentials.from_json(credstr)
    http = httplib2.Http()
    try:
        credentials.refresh(http)
    except oauth2client.client.AccessTokenCredentialsError:
        print "Refresh needed!"
        d = {"grant_type": "refresh_token", "client_secret": CLIENT_SECRET, "client_id": CLIENT_ID, "refresh_token": at['refresh_token']}
        resp, content = http.request("https://accounts.google.com/o/oauth2/token", "POST", body=urlencode(d), headers={'Content-type' : 'application/x-www-form-urlencoded'})
        credentials = AccessTokenCredentials(json.loads(content)['access_token'], 'python-jbocd/1.0')

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
            file = drive.files().get(fileId=sitem['id']).execute()
            download_url = file.get('downloadUrl')
            if download_url:
                resp, content = drive._http.request(download_url)
                if resp.status == 200:
                    out = open(sys.argv[3], 'wb')
                    out.write(content)
                    out.close()
                else:
                    print 'An error occurred: %s' % resp
                    sys.exit(1)
            sys.exit(0)
    
    sys.exit(1)
