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
    #h = httplib2.Http()
    #d = {"grant_type": "refresh_token", "client_secret": CLIENT_SECRET, "client_id": CLIENT_ID, "refresh_token": at['refresh_token']}
    #resp, content = h.request("https://accounts.google.com/o/oauth2/token", "POST", body=urlencode(d), headers={'Content-type' : 'application/x-www-form-urlencoded'})
    
    #credentials = AccessTokenCredentials(json.loads(content)['access_token'], 'python-jbocd/1.0')
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

    http = credentials.authorize(http)
    drive = build('drive', 'v2', http=http)

    strsplt = sys.argv[2][1:].split('/')
    filename = strsplt[len(strsplt)-1]
    strsplt = strsplt[:-1]
    cur_dir_id = 'root';
    
    try:
        for p in strsplt:
            param = {'q': "title = '%s' and '%s' in parents" % (p, cur_dir_id), 'fields':'items'}
            files = drive.files().list(**param).execute()
            #file_list = drive.ListFile({'fields':'items','q': "title = '%s' and '%s' in parents" % (p, cur_dir_id)}).GetList()
            if len(files['items']) == 0:
                print "Directory not found"
                sys.exit(404)
            else:
                cur_dir_id = files['items'][0]['id']

        param = {'q': "title = '%s' and '%s' in parents" % (filename, cur_dir_id), 'fields':'items'}
        files = drive.files().list(**param).execute()
        if len(files['items']) == 0:
            print "File not found"
            sys.exit(404)
        else:
            drive.files().delete(fileId=files['items'][0]['id']).execute()
            #drive.files().emptyTrash()
    except errors.HttpError, e:
        #print 'Error: %s' % e
        try:
            # Load Json body.
            error = simplejson.loads(e.content)
            print 'Error code: %d' % error.get('code')
            print 'Error message: %d' % error.get('message')
            sys.exit(error.get('code'))

            # More error information can be retrieved with error.get('errors').
        except TypeError:
            # Could not load Json body.
            print 'HTTP Status code: %d' % e.resp.status
            print 'HTTP Reason: %s' % e.resp.reason
            sys.exit(e.resp.status)
        except ValueError:
            # Could not load Json body.
            print 'HTTP Status code: %d' % e.resp.status
            print 'HTTP Reason: %s' % e.resp.reason
            sys.exit(e.resp.status)
    
    sys.exit(0)
