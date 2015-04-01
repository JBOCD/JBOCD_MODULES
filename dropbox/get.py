# Include the Dropbox SDK
import sys
import dropbox
import string
import ConfigParser

def PrintHelp():
    print "Python Dropbox Downloader"
    print "usage: python get.py [credentials] [remote file path] [local file path]"

if len(sys.argv) < 2 : print "Get.py: Access token cannot be null. (Argument 1)"
elif len(sys.argv) < 3 : print "Get.py: Please enter the file you want to download. (Argument 2)"
elif len(sys.argv) < 4 : print "Get.py: Please enter the local path. (Argument 3)"
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

    # Download file
    try:
        f, meta = client.get_file_and_metadata(sys.argv[2])
        out = open(sys.argv[3], 'wb')
        out.write(f.read())
        out.close()
    except dropbox.rest.ErrorResponse as e:
        print "Put Error: ", e.error_msg
        exit(1)
    
    sys.exit(0)
