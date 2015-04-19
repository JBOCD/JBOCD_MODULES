#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/wait.h>
#include "CDDriver.h"

class FTP: public CDDriver{
	private:
		static const char* lang;
		static const char* getCMD;
		static const char* putCMD;
		static const char* delCMD;
		char* conf;
	protected:
		unsigned int id;
	public:
		~FTP();
		FTP(const char* accessToken, unsigned int id);
		int get(char* remotefilePath, char* localfilePath);
		int put(char* remotefilePath, char* localfilePath);
		int del(char* remotefilePath);
		bool isID(unsigned int id);
		unsigned int getID();
};
