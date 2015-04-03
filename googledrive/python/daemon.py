from googleapi import GAPI
import sys,json,thread

gd = GAPI(sys.argv[1], sys.argv[2])

userinput = raw_input()
while userinput:
	try:
		current = json.loads(userinput)
		opID = current['opID']
		command = current['command']
		if gd.checkCredential() == False:
			gd.requestNewCredential()
		if command == 'put':
			thread.start_new_thread( gd.put,(current['local'], current['remote'], opID) )
		elif command == 'get':
			thread.start_new_thread( gd.get, (current['remote'], current['local'], opID) )
		elif command == 'delete':
			thread.start_new_thread( gd.delete, (current['remote'], opID) )
		userinput = raw_input()
	except EOFError:
		sys.exit(0)