import os
import sys
import simplejson
import string
import ConfigParser
import httplib2
import json
import oauth2client.client
import thread
from mimetypes import MimeTypes
from urllib import urlencode
from oauth2client.client import AccessTokenCredentials
from apiclient.discovery import build
from apiclient.http import MediaFileUpload
from apiclient import errors

class GAPI:
	def __init__(self, json):
		self.dir_id = {}
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
		self.working_dir = 'root'
		self.lock = thread.allocate_lock()

	def directoryID(self, wd):
		strsplt = wd[1:].split('/')
		remote = strsplt[-1]
		strsplt = strsplt[:-1]
		wdir = "/"+"/".join(strsplt)
		with self.lock:
			try:
				working_dir = self.dir_id[wdir]
			except KeyError:
				#print >> sys.stderr, "INFO: ", "Check directory"
				drive = self.getNewDrive()
				#print >> sys.stderr, "INFO: ", "Checking %s" % wdir
				working_dir = 'root'
				try:
					working_dir = 'root'
					for p in strsplt:
						param = {'q': "title = '%s' and '%s' in parents" % (p, working_dir), 'fields':'items'}
						files = drive.files().list(**param).execute()
						if len(files['items']) == 0:
							d = drive.files().insert(body={'title': p, "mimeType": "application/vnd.google-apps.folder", 'parents':[{'id': working_dir}]}).execute()
							working_dir = d['id']
							#print "Created Working DIR: ",=
							#print d
						else:
							working_dir = files['items'][0]['id']
							#print "Working DIR: "
							#print files['items'][0]
					self.dir_id[wdir] = working_dir
					#print "working_dir ID=", self.working_dir
				except errors.HttpError, e:
					#print 'Error: %s' % e
					try:
						# Load Json body.
						error = json.loads(e.content)
						#print 'Error code: %d' % error.get('code')
						#print 'Error message: %d' % error.get('message')
						print >> sys.stderr, error['error']['code']
						# More error information can be retrieved with error.get('errors').
					except TypeError:
						# Could not load Json body.
						#print 'HTTP Status code: %d' % e.resp.status
						#print 'HTTP Reason: %s' % e.resp.reason
						print >> sys.stderr, e.resp.status
					except ValueError:
						# Could not load Json body.
						#print 'HTTP Status code: %d' % e.resp.status
						#print 'HTTP Reason: %s' % e.resp.reason
						print >> sys.stderr, e.resp.status
		return remote, working_dir

	def getDir(self, wd):
		strsplt = wd[1:].split('/')
		remote = strsplt[-1]
		strsplt = strsplt[:-1]
		wdir = "/"+"/".join(strsplt)
		with self.lock:
			try:
				working_dir = self.dir_id[wdir]
			except KeyError:
				try:
					drive = self.getNewDrive()
					working_dir = 'root'
					for p in strsplt:
						param = {'q': "title = '%s' and '%s' in parents" % (p, working_dir), 'fields':'items'}
						files = drive.files().list(**param).execute()
						if len(files['items']) == 0:
							working_dir = d['id']
							status = 404
							return remote, working_dir, status
							#print "Created Working DIR: ",=
							#print d
						else:
							working_dir = files['items'][0]['id']
							#print "Working DIR: "
							#print files['items'][0]
					self.dir_id[wdir] = working_dir
					#print "working_dir ID=", self.working_dir
				except errors.HttpError, e:
					#print 'Error: %s' % e
					try:
						# Load Json body.
						error = json.loads(e.content)
						#print 'Error code: %d' % error.get('code')
						#print 'Error message: %d' % error.get('message')
						print >> sys.stderr, error['error']['code']
						# More error information can be retrieved with error.get('errors').
					except TypeError:
						# Could not load Json body.
						#print 'HTTP Status code: %d' % e.resp.status
						#print 'HTTP Reason: %s' % e.resp.reason
						print >> sys.stderr, e.resp.status
					except ValueError:
						# Could not load Json body.
						#print 'HTTP Status code: %d' % e.resp.status
						#print 'HTTP Reason: %s' % e.resp.reason
						print >> sys.stderr, e.resp.status
		return remote, working_dir, None

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
		filename, working_dir = self.directoryID(remote)
		body = {
			'title': filename,
			'description': "Uploaded by python-jbocd",
			'parents':[{'id': working_dir}]
			#'mimeType' : mt
		}
		media_body = MediaFileUpload(local, 'application/octet-stream')
		try:
			param = {'q': "title = '%s' and '%s' in parents" % (filename, working_dir), 'fields':'items'}
			try:
				files = drive.files().list(**param).execute()
			except errors.HttpError, e:
				if e.resp.status == 401 and self.checkCredential() == False:
					self.requestNewCredential()
					files = drive.files().list(**param).execute()
			
			if len(files['items']) > 0:
				#print "Updated"
				drive.files().update(fileId=files['items'][0]['id'], body=body, media_body=media_body, newRevision=True).execute()
			else:
				#print 'Uploaded'
				drive.files().insert(body=body, media_body=media_body).execute()
			print '{} {}\n'.format(op, 0)
		except errors.HttpError, e:
			#print 'Error: %s' % e
			try:
       				# Load Json body.
				error = json.loads(e.content)
				#print 'Error code: %d' % error.get('code')
				#print 'Error message: %d' % error.get('message')
				#print >> sys.stderr, error.get('message')
				print '{} {}\n'.format(op, error['error']['code'])
				# More error information can be retrieved with error.get('errors').
			except TypeError:
				# Could not load Json body.
				#print 'HTTP Status code: %d' % e.resp.status
				#print 'HTTP Reason: %s' % e.resp.reason
				print '{} {}\n'.format(op, e.resp.status)
			except ValueError:
				# Could not load Json body.
				#print 'HTTP Status code: %d' % e.resp.status
				#print 'HTTP Reason: %s' % e.resp.reason
				print '{} {}\n'.format(op, e.resp.status)
		sys.stdout.flush()

	def get(self, remote, local, op):
		drive = self.getNewDrive()
		filename, working_dir, status = self.getDir(remote)
		if status != None:
			print '{} {}\n'.format(op, 404)
		elif filename == None:
			print '{} {}\n'.format(op, 404)
		else:
			try:
				param = {'q': "title = '%s' and '%s' in parents" % (filename, working_dir), 'fields':'items'}
				try:
					files = drive.files().list(**param).execute()
				except errors.HttpError, e:
					if e.resp.status == 401 and self.checkCredential() == False:
						self.requestNewCredential()
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
							print '{} {}\n'.format(op, 0)
						else:
							#print 'An error occurred: %s' % resp
							print '{} {}\n'.format(op, 500)
					else:
						#print 'An error occurred: %s' % resp
						print '{} {}\n'.format(op, 500)
				else:
					#print 'Uploaded'
					#print "File not found"
					print '{} {}\n'.format(op, 404)
	
			except errors.HttpError, e:
				#print 'Error: %s' % e
				try:
					# Load Json body.
					error = json.loads(e.content)
					#print 'Error code: %d' % error.get('code')
					#print 'Error message: %d' % error.get('message')
					print '{} {}\n'.format(op, error['error']['code'])
					# More error information can be retrieved with error.get('errors').
				except TypeError:
					# Could not load Json body.
					#print 'HTTP Status code: %d' % e.resp.status
					#print 'HTTP Reason: %s' % e.resp.reason
					print '{} {}\n'.format(op, e.resp.status)
				except ValueError:
					# Could not load Json body.
					#print 'HTTP Status code: %d' % e.resp.status
					#print 'HTTP Reason: %s' % e.resp.reason
					print '{} {}\n'.format(op, e.resp.status)
		sys.stdout.flush()

	def delete(self, remote, op):
		drive = self.getNewDrive()
		filename, working_dir, status = self.getDir(remote)
		if filename == None or status != None:
			print '{} {}\n'.format(op, 404)
		else:
			try:
				param = {'q': "title = '%s' and '%s' in parents" % (filename, working_dir), 'fields':'items'}
				try:
					files = drive.files().list(**param).execute()
				except errors.HttpError, e:
					if e.resp.status == 401 and self.checkCredential() == False:
						self.requestNewCredential()
						files = drive.files().list(**param).execute()
			
				if len(files['items']) > 0:
					#print "Updated"
					drive.files().delete(fileId=files['items'][0]['id']).execute()
					print '{} {}\n'.format(op, 0)
					#print 'Uploaded'
					#print "File not found"
				else:
					print '{} {}\n'.format(op, 404)
				
			except errors.HttpError, e:
				#print 'Error: %s' % e
				try:
					# Load Json body.
					error = json.loads(e.content)
					#print 'Error code: %d' % error.get('code')
					#print 'Error message: %d' % error.get('message')
					print '{} {}\n'.format(op, error['error']['code'])
					# More error information can be retrieved with error.get('errors').
				except TypeError:
					# Could not load Json body.
					#print 'HTTP Status code: %d' % e.resp.status
					#print 'HTTP Reason: %s' % e.resp.reason
					print '{} {}\n'.format(op, e.resp.status)
				except ValueError:
					# Could not load Json body.
					#print 'HTTP Status code: %d' % e.resp.status
					#print 'HTTP Reason: %s' % e.resp.reason
					print '{} {}\n'.format(op, e.resp.status)
		sys.stdout.flush()
