# Include the Dropbox SDK
import sys
import dropbox
import ConfigParser

def PrintHelp():
    print "Python Dropbox Uploader"
    print "usage: python put.py [credentials] [local file path] [remote file path]"

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
    Config.read("/var/JBOCD/module/dropbox/config.ini")

    # Get your app key and secret from the Dropbox developer website
    app_key = ConfigSectionMap("dropbox")['appkey']
    app_secret = ConfigSectionMap("dropbox")['appsecret']
    client = dropbox.client.DropboxClient(sys.argv[1])

    # Get filepath
    #print "Uploading: " + sys.argv[1]

    #print 'linked account: ', client.account_info()

    # Open file
    f = open(sys.argv[2], 'rb')
    try:
        response = client.put_file(sys.argv[3], f, True)
    except dropbox.rest.ErrorResponse as e:
        print "Put Error: ", e.error_msg
        print "\tStatus: ", e.status
        print "\tReason: ", e.reason
        print "\tuser_error_msg: ", e.user_error_msg
        exit(e.status)
    
    sys.exit(0)
