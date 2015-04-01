# Include the Dropbox SDK
import sys
import dropbox
import ConfigParser

print "###",sys.argv[2]

def PrintHelp():
    print "Python Dropbox Deleter"
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
    Config.read("/var/JBOCD/module/dropbox/config.ini")

    # Get your app key and secret from the Dropbox developer website
    app_key = ConfigSectionMap("dropbox")['appkey']
    app_secret = ConfigSectionMap("dropbox")['appsecret']
    client = dropbox.client.DropboxClient(sys.argv[1])

    # Get filepath
    #print "Uploading: " + sys.argv[1]

    #print 'linked account: ', client.account_info()

    # Delete file
    try:
        response = client.file_delete(sys.argv[2])
    except dropbox.rest.ErrorResponse as e:
        if e.status == 404:
            print "Delete Error: File not found!"
        else:
            print "Delete Error: ", e.error_msg
        exit(e.status)
    
    sys.exit(0)
