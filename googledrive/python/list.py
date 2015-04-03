#!/usr/bin/python

# Include the Google Drive SDK
import os
import sys
import string
import ConfigParser
import httplib2
import oauth2client.client

import json
from urllib import urlencode
from oauth2client.client import AccessTokenCredentials
from apiclient.discovery import build
from apiclient import errors


# Configuration
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

Config = ConfigParser.ConfigParser()
Config.read("./config.ini")
CLIENT_ID = ConfigSectionMap("googledrive")['clientid']
CLIENT_SECRET = ConfigSectionMap("googledrive")['clientsecret']
REDIRECT_URI = "urn:ietf:wg:oauth:2.0:oob"
SCOPES = ['https://www.googleapis.com/auth/drive']

def PrintHelp():
    print "Python Google Drive Directory Lister"
    print "usage: python list.py [access token] [local file path] [directory path = '/'']"

if len(sys.argv) < 2 : print "list.py: Access token cannot be null. (Argument 1)"
elif len(sys.argv) < 3 :   print "list.py: Local file path cannot be null. (Argument 2)"
elif len(sys.argv) < 4 :
#	at = simplejson.loads(sys.argv[1])
	at = json.loads(sys.argv[1])
	#h =  httplib2.Http()
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
	
	try:
		list = drive.files().list(q='\'root\' in parents').execute()
		# list = drive.files().list().execute()
	except Exception as e:
		print "###", e.message, "(", e.args, ")"
		exit(1)
	
	#print list
	
	dir_list = {}
	for item in list['items']:
		if item["labels"]["trashed"] == False:
			if item['mimeType'] == 'application/vnd.google-apps.folder':
				dir_list[item['title']] = "directory"
			else:
				mime, type = item['mimeType'].split('/')
				dir_list[item['title']] = type
	
	out = open(sys.argv[2], 'wb')
	out.write(json.dumps(dir_list)+"\n")
	out.close()

	sys.exit(0)
	
	#print list['pageToken']
	
# elif len(sys.argv) < 4 : 
    # at = simplejson.loads(sys.argv[1])
    # h = httplib2.Http()
    # d = {"grant_type": "refresh_token", "client_secret": CLIENT_SECRET, "client_id": CLIENT_ID, "refresh_token": at['refresh_token']}
    # resp, content = h.request("https://accounts.google.com/o/oauth2/token", "POST", body=urlencode(d), headers={'Content-type' : 'application/x-www-form-urlencoded'})
	
    # credentials = AccessTokenCredentials(json.loads(content)['access_token'], 'python-jbocd/1.0')
    

    # http = httplib2.Http()
    # http = credentials.authorize(http)
    # drive = build('drive', 'v2', http=http)

    # try:
        # list = drive.files().list().execute()
    # except AccessTokenCredentialsError as e:
        # print "###", e.message, "(", e.args, ")"
        # exit(1)

    # root = drive.about().get().execute()['rootFolderId']
    # dir_list = {}
    # for item in list['items']:
        # if item['labels']['trashed'] == False:
            # if item['mimeType'] == 'application/vnd.google-apps.folder':
                # for parent in item['parents']:
                    # if parent['id'] == root:
                        # dir_list[item['title']] = "directory"
                        # break
            # else:
                # for parent in item['parents']:
                    # if parent['id'] == root:
                        # mime, type = item['mimeType'].split('/')
                        # dir_list[item['title']] = type
                        # break

    # out = open(sys.argv[2], 'wb')
    # out.write(json.dumps(dir_list) + "\n")
    # out.close()

    # sys.exit(0)
else:
	at = simplejson.loads(sys.argv[1])
	h = httplib2.Http()
	d = {"grant_type": "refresh_token", "client_secret": CLIENT_SECRET, "client_id": CLIENT_ID, "refresh_token": at['refresh_token']}
	resp, content = h.request("https://accounts.google.com/o/oauth2/token", "POST", body=urlencode(d), headers={'Content-type' : 'application/x-www-form-urlencoded'})
	
	credentials = AccessTokenCredentials(json.loads(content)['access_token'], 'python-jbocd/1.0')
	http = httplib2.Http()
	http = credentials.authorize(http)
	drive = build('drive', 'v2', http=http)

	root = drive.about().get().execute()['rootFolderId']
	str = sys.argv[3]
	cur = root

	if str != '/':
		strsplt = str[1:].split('/')

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

		if drive.files().get(fileId=cur).execute()['title'] != strsplt[len(strsplt)-1]:
			print "Directory not found!"
			exit(1)

	dir_list = {}
	target = drive.children().list(folderId=cur).execute()
	for item in target['items']:
		sitem = drive.files().get(fileId=item['id']).execute()
		if sitem["labels"]["trashed"] == False:
			if sitem["mimeType"] == "application/vnd.google-apps.folder":
				dir_list[sitem['title']] = "directory"
				#print sitem['title'], "(Directory)"
			else:
				mime, type = sitem['mimeType'].split('/')
				dir_list[sitem['title']] = type
				#print sitem['title'], "(",type,")"
				
	out = open(sys.argv[2], 'wb')
	out.write(json.dumps(dir_list)+"\n")
	out.close()

	sys.exit(0)
