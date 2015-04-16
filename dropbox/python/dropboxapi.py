# Include the Dropbox SDK
import sys
import dropbox
import ConfigParser

class DropboxAPI:
	def __init__(self, json):
		Config = ConfigParser.ConfigParser()
		Config.read("/var/JBOCD/module/dropbox/config.ini")
		# Get your app key and secret from the Dropbox developer website
		app_key = self.ConfigSectionMap("dropbox", Config)['appkey']
		app_secret = self.ConfigSectionMap("dropbox", Config)['appsecret']

		self.drop = dropbox.client.DropboxClient(json)
		
	def ConfigSectionMap(self, section, Config):
		dict1 = {}
		options = Config.options(section)
		for option in options:
			try:
				dict1[option] = Config.get(section, option)
				#if dict1[option] == -1:
					#DebugPrint("skip: %s" % option)
			except:
				#print("exception on %s!" % option)
				dict1[option] = None
		return dict1

	def put(self, local, remote, op):
		try:
			f = open(local, 'rb')
			response = self.drop.put_file(remote, f, True)
			print '{} {}\n'.format(op, 0)
		except dropbox.rest.ErrorResponse as e:
			#print "Put Error: ", e.error_msg
			#print "\tStatus: ", e.status
			#print "\tReason: ", e.reason
			#print "\tuser_error_msg: ", e.user_error_msg
			print '{} {}\n'.format(op, e.status)
		except:
			print >> sys.stderr, 'Handle Unknown error (ReadTimeoutError).\n'
			print '{} {}\n'.format(op, 1)
		sys.stdout.flush()

	def get(self, remote, local, op):
		try:
			f, meta = self.drop.get_file_and_metadata(remote)
			out = open(local, 'wb')
			out.write(f.read())
			out.close()
			print '{} {}\n'.format(op, 0)
		except dropbox.rest.ErrorResponse as e:
			#print "Put Error: ", e.error_msg
			print '{} {}\n'.format(op, e.status)
		except:
			print '{} {}\n'.format(op, 1)
		sys.stdout.flush()

	def delete(self, remote, op):
		try:
			response = self.drop.file_delete(remote)
			print '{} {}\n'.format(op, 0)
		except dropbox.rest.ErrorResponse as e:
			#print "Delete Error: ", e.error_msg
			#print "\tStatus: ", e.status
			#print "\tReason: ", e.reason
			#print "\tuser_error_msg: ", e.user_error_msg
			print '{} {}\n'.format(op, e.status)
		except:
			print '{} {}\n'.format(op, 1)
		sys.stdout.flush()
