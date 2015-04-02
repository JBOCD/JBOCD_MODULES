# Include the Google Drive SDK
import os
import sys
import simplejson
import string
import ConfigParser
import httplib2
import json
from mimetypes import MimeTypes
from urllib import urlencode
from oauth2client.client import AccessTokenCredentials
from apiclient.discovery import build
from apiclient.http import MediaFileUpload
from apiclient import errors

def PrintHelp():
    print "Python Google Drive Uploader"
    print "usage: python put.py [access token] [local file path] [remote file path]"

mt = MimeTypes();


if len(sys.argv) < 2 : print "Put.py: Access token cannot be null. (Argument 1)"
elif len(sys.argv) < 3 : print "Put.py: Please enter the file you want to upload. (Argument 2)"
elif len(sys.argv) < 4 : print "Put.py: Please enter the remote path. (Argument 3)"
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

    #gauth = GoogleAuth()
    credentials = AccessTokenCredentials(json.loads(content)['access_token'], 'python-jbocd/1.0')

    #drive = GoogleDrive(gauth)

    #file_list = drive.ListFile({'q': "'root' in parents"}).GetList()
    
    #print file_list

    http = httplib2.Http()
    http = credentials.authorize(http)
    drive = build('drive', 'v2', http=http)

    #root = drive.about().get().execute()['rootFolderId']
    #str = sys.argv[3]
    #cur = root
    strsplt = sys.argv[3][1:].split('/')[:]
    filename = strsplt[len(strsplt)-1]
    strsplt = strsplt[:-1]
    cur_dir_id = 'root';
    

    for p in strsplt:
        param = {'q': "title = '%s' and '%s' in parents" % (p, cur_dir_id), 'fields':'items'}
        files = drive.files().list(**param).execute()
        #file_list = drive.ListFile({'fields':'items','q': "title = '%s' and '%s' in parents" % (p, cur_dir_id)}).GetList()
        if len(files['items']) == 0:
            d = drive.files().insert(body={'title': p, "mimeType": "application/vnd.google-apps.folder", 'parents':[{'id': cur_dir_id}]}).execute()
            cur_dir_id = d['id']
        else:
            cur_dir_id = files['items'][0]['id']

    mt = mt.guess_type(sys.argv[2])[0]
    body = {
        'title': filename,
        'description': "Uploaded by python-jbocd",
        'parents':[{'id': cur_dir_id}]
        #'mimeType' : mt
    }
    
    media_body = MediaFileUpload(sys.argv[2], 'application/octet-stream')

    try:
        param = {'q': "title = '%s' and '%s' in parents" % (filename, cur_dir_id), 'fields':'items'}
        files = drive.files().list(**param).execute()
        if len(files['items']) > 0:
            print "Updated"
            drive.files().update(fileId=files['items'][0]['id'], body=body, media_body=media_body, newRevision=True).execute()
        else:
            print 'Uploaded'
            drive.files().insert(body=body, media_body=media_body).execute()
        
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
