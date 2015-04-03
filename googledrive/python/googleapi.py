import os
import sys
import simplejson
import string
import ConfigParser
import httplib2
import json
import oauth2client.client
from mimetypes import MimeTypes
from urllib import urlencode
from oauth2client.client import AccessTokenCredentials
from apiclient.discovery import build
from apiclient.http import MediaFileUpload
from apiclient import errors

class GAPI:
	def __init__(self, json, working_dir):
		self.REDIRECT_URI = "urn:ietf:wg:oauth:2.0:oob"
		self.SCOPES = ['https://www.googleapis.com/auth/drive']

		Config = ConfigParser.ConfigParser()
		Config.read("/var/JBOCD/module/googledrive/config.ini")
		self.CLIENT_ID = self.ConfigSectionMap("googledrive", Config)['clientid']
		self.CLIENT_SECRET = self.ConfigSectionMap("googledrive", Config)['clientsecret']
		self.at = simplejson.loads(json)
		credential_json = '{"_module": "oauth2client.client", "token_expiry": null, "access_token": null, "token_uri": null, "invalid": false, "token_response": null, "client_id": "%s", "id_token": null, "client_secret": "%s", "revoke_uri": null, "_class": "AccessTokenCredentials", "refresh_token": "%s", "user_agent": "python-jbocd/1.0"}' % (  self.CLIENT_ID, self.CLIENT_SECRET, self.at['refresh_token'])
		
		#self.http = httplib2.Http()
		self.requestNewCredential()
		#authhttp = self.credentials.authorize(self.http)
		#self.drive = build('drive', 'v2', http=authhttp)
		drive = self.getNewDrive()

		strsplt = working_dir[1:].split('/')
		strsplt = strsplt[:]
		self.working_dir = 'root';

		for p in strsplt:
			param = {'q': "title = '%s' and '%s' in parents" % (p, self.working_dir), 'fields':'items'}
			files = drive.files().list(**param).execute()
			if len(files['items']) == 0:
				d = drive.files().insert(body={'title': p, "mimeType": "application/vnd.google-apps.folder", 'parents':[{'id': self.working_dir}]}).execute()
				self.working_dir = d['id']
				#print "Created Working DIR: ",=
				#print d
			else:
				self.working_dir = files['items'][0]['id']
				#print "Working DIR: "
				#print files['items'][0]
		#print "working_dir ID=", self.working_dir

	def getNewDrive(self):
		http = httplib2.Http()
		authhttp = self.credentials.authorize(http)
		return build('drive', 'v2', http=authhttp)

	def checkCredential(self):
		try:
			http = httplib2.Http()
			self.credentials.refresh(http)
		except oauth2client.client.AccessTokenCredentialsError:
			return False
		return True

	def requestNewCredential(self):
		http = httplib2.Http()
		d = {"grant_type": "refresh_token", "client_secret": self.CLIENT_SECRET, "client_id": self.CLIENT_ID, "refresh_token": self.at['refresh_token']}
		resp, content = http.request("https://accounts.google.com/o/oauth2/token", "POST", body=urlencode(d), headers={'Content-type' : 'application/x-www-form-urlencoded'})
		self.credentials = AccessTokenCredentials(json.loads(content)['access_token'], 'python-jbocd/1.0')
		
	def ConfigSectionMap(self, section, Config):
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

	def put(self, local, remote, op):
		drive = self.getNewDrive()
		body = {
			'title': remote,
			'description': "Uploaded by python-jbocd",
			'parents':[{'id': self.working_dir}]
			#'mimeType' : mt
		}
		media_body = MediaFileUpload(local, 'application/octet-stream')
		try:
			param = {'q': "title = '%s' and '%s' in parents" % (remote, self.working_dir), 'fields':'items'}
			files = drive.files().list(**param).execute()
			if len(files['items']) > 0:
				#print "Updated"
				drive.files().update(fileId=files['items'][0]['id'], body=body, media_body=media_body, newRevision=True).execute()
			else:
				#print 'Uploaded'
				drive.files().insert(body=body, media_body=media_body).execute()
		except errors.HttpError, e:
			#print 'Error: %s' % e
			try:
				# Load Json body.
				error = simplejson.loads(e.content)
				#print 'Error code: %d' % error.get('code')
				#print 'Error message: %d' % error.get('message')
				print op, error.get('code')
				# More error information can be retrieved with error.get('errors').
			except TypeError:
				# Could not load Json body.
				#print 'HTTP Status code: %d' % e.resp.status
				#print 'HTTP Reason: %s' % e.resp.reason
				print op, e.resp.status
			except ValueError:
				# Could not load Json body.
				#print 'HTTP Status code: %d' % e.resp.status
				#print 'HTTP Reason: %s' % e.resp.reason
				print op, e.resp.status
			return 0
		print op, 0

	def get(self, remote, local, op):
		drive = self.getNewDrive()
		try:
			param = {'q': "title = '%s' and '%s' in parents" % (remote, self.working_dir), 'fields':'items'}
			files = drive.files().list(**param).execute()
			if len(files['items']) > 0:
				#print "Updated"
				file = drive.files().get(fileId=files['items'][0]['id']).execute()
				download_url = file.get('downloadUrl')
				if download_url:
					resp, content = drive._http.request(download_url)
					if resp.status == 200:
						out = open(local, 'wb')
						out.write(content)
						out.close()
					else:
						#print 'An error occurred: %s' % resp
						print op, 500
			else:
				#print 'Uploaded'
				#print "File not found"
				print op, 404
		except errors.HttpError, e:
			#print 'Error: %s' % e
			try:
				# Load Json body.
				error = simplejson.loads(e.content)
				#print 'Error code: %d' % error.get('code')
				#print 'Error message: %d' % error.get('message')
				print op, error.get('code')
				# More error information can be retrieved with error.get('errors').
			except TypeError:
				# Could not load Json body.
				#print 'HTTP Status code: %d' % e.resp.status
				#print 'HTTP Reason: %s' % e.resp.reason
				print op, e.resp.status
			except ValueError:
				# Could not load Json body.
				#print 'HTTP Status code: %d' % e.resp.status
				#print 'HTTP Reason: %s' % e.resp.reason
				print op, e.resp.status
			return 0
		print op, 0

	def delete(self, remote, op):
		drive = self.getNewDrive()
		try:
			param = {'q': "title = '%s' and '%s' in parents" % (remote, self.working_dir), 'fields':'items'}
			files = drive.files().list(**param).execute()
			if len(files['items']) > 0:
				#print "Updated"
				drive.files().delete(fileId=files['items'][0]['id']).execute()
			else:
				#print 'Uploaded'
				#print "File not found"
				print op, 0
		except errors.HttpError, e:
			#print 'Error: %s' % e
			try:
				# Load Json body.
				error = simplejson.loads(e.content)
				#print 'Error code: %d' % error.get('code')
				#print 'Error message: %d' % error.get('message')
				print op, error.get('code')
				# More error information can be retrieved with error.get('errors').
			except TypeError:
				# Could not load Json body.
				#print 'HTTP Status code: %d' % e.resp.status
				#print 'HTTP Reason: %s' % e.resp.reason
				print op, e.resp.status
			except ValueError:
				# Could not load Json body.
				#print 'HTTP Status code: %d' % e.resp.status
				#print 'HTTP Reason: %s' % e.resp.reason
				print op, e.resp.status
			return 0
		print op, 0

