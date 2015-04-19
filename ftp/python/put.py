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
	try:
		ftp.storbinary('STOR %s' % sys.argv[2], open(sys.argv[3], 'rb'))
	except:
		strsplt = sys.argv[2][1:].split('/')
		strsplt = strsplt[:-1]
		wdir = "/"+"/".join(strsplt)
		ftp.mkd(wdir)
		ftp.storbinary('STOR %s' % sys.argv[2], open(sys.argv[3], 'rb'))
	ftp.quit()
except:
	sys.exit(1)
