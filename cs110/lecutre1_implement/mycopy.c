#include<unistd.h>
#include<stdio.h>
#include<stdbool.h>
#include<fcntl.h>
#include <errno.h>
#include<stdlib.h>

static const int AurgmentNumError=1;
static const int FileReadError=2;
static const int kDefaultPermissions = 0644; // number equivalent of "rw-r--r--"
static const int FileExistError=4;

int main(int argc,char *argv[]){
  if(argc!=3){
      fprintf (stderr,"You must use the form 'copy src dest' ");
      exit(AurgmentNumError);
    }
  int fdin=open(argv[1],O_RDONLY);
  if(fdin==-1) exit(FileReadError);
  int fdout=open(argv[2],O_CREAT|O_WRONLY|O_EXCL,kDefaultPermissions);
  if(fdout==-1){
      if(errno==EEXIST)
        fprintf (stderr,"dest file exited! copy failed. \n");
      exit(FileExistError);
    }
  char buffer[1024];
  while (true) {
      int readInAmount=read (fdin,buffer,1024);
      if(readInAmount==0) break;
      if(readInAmount==-1) fprintf (stderr,"Can't access the src-file!");
      int writenAmount=0;
      while (writenAmount!=readInAmount) {
          int writenIn=write(fdout,buffer+writenAmount,readInAmount-writenAmount);
          writenAmount+=writenIn;
        }
    }
  close (fdin);
  close (stdout);
  return 0;

}