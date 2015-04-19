#include "FTP.h"
const char* FTP::lang   ="python";
const char* FTP::getCMD ="/var/JBOCD/module/ftp/get.py";
const char* FTP::putCMD ="/var/JBOCD/module/ftp/put.py";
const char* FTP::delCMD ="/var/JBOCD/module/ftp/del.py";

FTP::FTP(const char* conf, unsigned int id){
	int len = strlen(conf);
	this->conf = (char*) malloc(len+1);
	strcpy(this->conf, conf);
	this->id = id;
}
int FTP::get(char* remotefilePath, char* localfilePath){
	pid_t pid;
	int status;
	if( (pid = fork()) ){
		waitpid(pid, &status, 0);
	}else{
		execlp(lang, lang, getCMD, conf, remotefilePath, localfilePath, NULL);
		printf("[%u] Fail to open script\n", getpid());
		exit(1);
	}
	return WEXITSTATUS(status);
}
int FTP::put(char* remotefilePath, char* localfilePath){
	pid_t pid;
	int status;
	if( (pid = fork()) ){
		waitpid(pid, &status, 0);
	}else{
		execlp(lang, lang, putCMD, conf, remotefilePath, localfilePath, NULL);
		printf("[%u] Fail to open script\n", getpid());
		exit(1);
	}
	return WEXITSTATUS(status);
}
int FTP::del(char* remotefilePath){
	pid_t pid;
	int status;
	if( (pid = fork()) ){
		waitpid(pid, &status, 0);
	}else{
		execlp(lang, lang, delCMD, conf, remotefilePath, NULL);
		printf("[%u] Fail to open script\n", getpid());
		exit(1);
	}
	return WEXITSTATUS(status);
}
bool FTP::isID(unsigned int id){
	return this->id == id;
}
unsigned int FTP::getID(){
	return this->id;
}

FTP::~FTP(){
	if(conf){
		free(conf);
		conf = 0;
	}
}

CDDriver* createObject(const char* conf, unsigned int id){
	return new FTP(conf, id);
}

