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
				if dict1[option] == -1:
					#DebugPrint("skip: %s" % option)
			except:
				#print("exception on %s!" % option)
				dict1[option] = None
		return dict1

	def put(self, local, remote, op):
		try:
			f = open(local, 'rb')
			response = self.drop.put_file(remote, f, True)
		except dropbox.rest.ErrorResponse as e:
			#print "Put Error: ", e.error_msg
			#print "\tStatus: ", e.status
			#print "\tReason: ", e.reason
			#print "\tuser_error_msg: ", e.user_error_msg
			print op, e.status
			sys.stdout.flush()
			return 0
		print op, 0
		sys.stdout.flush()

	def get(self, remote, local, op):
		try:
			f, meta = self.drop.get_file_and_metadata(remote)
			out = open(local, 'wb')
			out.write(f.read())
			out.close()
		except dropbox.rest.ErrorResponse as e:
			#print "Put Error: ", e.error_msg
			print op, e.status
			sys.stdout.flush()
			return 0
		print op, 0
		sys.stdout.flush()

	def delete(self, remote, op):
		try:
			response = self.drop.file_delete(remote)
		except dropbox.rest.ErrorResponse as e:
			#print "Delete Error: ", e.error_msg
			#print "\tStatus: ", e.status
			#print "\tReason: ", e.reason
			#print "\tuser_error_msg: ", e.user_error_msg
			print op, e.status
			sys.stdout.flush()
			return 0
		print op, 0
		sys.stdout.flush()
