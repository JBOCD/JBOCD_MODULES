# Include the Dropbox SDK
import sys
import json
import string
import dropbox
import ConfigParser

def PrintHelp():
    print "Python Dropbox Directory Lister"
    print "usage: python list.py [access token] [local file path] [remote directory path = '/']"

if len(sys.argv) < 2 : print "list.py: Access token cannot be null. (Argument 1)"
elif len(sys.argv) < 3 : print "list.py: local file path cannot be null. (Argument 2)"
elif len(sys.argv) < 4 : 
    rdir = "/"
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
    Config.read("./config.ini")

    # Get your app key and secret from the Dropbox developer website
    app_key = ConfigSectionMap("dropbox")['appkey']
    app_secret = ConfigSectionMap("dropbox")['appsecret']
    client = dropbox.client.DropboxClient(sys.argv[1])

    # Get filepath
    #print "Uploading: " + sys.argv[1]

    #print 'linked account: ', client.account_info()

    # fetch dir list
    try:
        meta = client.metadata(rdir)
    except dropbox.rest.ErrorResponse as e:
        print "Fetch Error: ", e.error_msg
        exit(1)

    dir_list = {}
    for content in meta['contents']:
        if content['is_dir']:
            dir_list[string.replace(content['path'], rdir, '', 1)] = "directory"
        else:
            dir_list[string.replace(content['path'], rdir, '', 1)] = content["mime_type"]
    
    out = open(sys.argv[2], 'wb')
    out.write(json.dumps(dir_list) + "\n")
    out.close()

    sys.exit(0)
else:
    rdir = sys.argv[3]
    print "RDIR: ", rdir
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

    if rdir != "/":
        rdir = rdir + '/'

    # fetch dir list
    try:
        meta = client.metadata(rdir)
    except dropbox.rest.ErrorResponse as e:
        print "Fetch Error: ", e.error_msg
        sys.exit(1)

    dir_list = {}
    for content in meta['contents']:
        if content['is_dir']:
            dir_list[string.replace(content['path'], rdir, '', 1)] = "directory"
        else:
            dir_list[string.replace(content['path'], rdir, '', 1)] = content["mime_type"]
    
    out = open(sys.argv[2], 'wb')
    out.write(json.dumps(dir_list) + "\n")
    out.close()

    sys.exit(0)
