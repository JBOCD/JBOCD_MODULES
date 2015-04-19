import sys,json
server = json.loads(sys.argv[1])

try:
	if server['secure'] == True:
		from ftplib import FTP_TLS
		ftp = FTP_TLS()
	else:
		from ftplib import FTP
		ftp = FTP()
	ftp.connect(server['host'], server['port'])
	ftp.login(server['user'], server['pass'])
	ftp.retrbinary('RETR %s' % sys.argv[2], open(sys.argv[3], 'wb').write)
	ftp.quit()
except:
	sys.exit(1)
