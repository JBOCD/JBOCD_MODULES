from googleapi import GAPI
import sys,json

gd = GAPI(sys.argv[1], sys.argv[2])

userinput = raw_input()
while userinput:
	try:
		current = json.loads(userinput)
		opID = current['opID']
		command = current['command']
		if command == 'put':
			print opID, gd.put(current['local'], current['remote'])
		elif command == 'get':
			print opID, gd.get(current['remote'], current['local'])
		elif command == 'delete':
			print opID, gd.delete(current['remote'])
		userinput = raw_input()
	except EOFError:
		sys.exit(0)