from dropboxapi import DropboxAPI
import sys,json,thread

gd = DropboxAPI(sys.argv[1])

userinput = raw_input()
while userinput:
	try:
		current = json.loads(userinput)
		opID = current['opID']
		command = current['command']
		if command == 'put':
			thread.start_new_thread( gd.put, (current['local'], current['remote'], opID) )
		elif command == 'get':
			thread.start_new_thread( gd.get, (current['remote'], current['local'], opID) )
		elif command == 'delete':
			thread.start_new_thread( gd.delete, (current['remote'], opID) )
		userinput = raw_input()
	except EOFError:
		sys.exit(0)