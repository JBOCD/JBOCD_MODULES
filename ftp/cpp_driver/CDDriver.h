#ifndef CDDRIVER_H
#define CDDRIVER_H

class CDDriver{
	private:
	protected:
		CDDriver(){}
	public:
		virtual ~CDDriver(){}
		virtual int get(char* remotefilePath, char* localfilePath) = 0;	// return exit code
		virtual int put(char* remotefilePath, char* localfilePath) = 0;	// return exit code
		virtual int del(char* remotefilePath) = 0;	// return exit code
		virtual bool isID(unsigned int id) = 0;
		virtual unsigned int getID() = 0;
};

extern "C" CDDriver* createObject(const char*, unsigned int);

#endif
