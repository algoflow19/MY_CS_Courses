#include <ctype.h>
#include <errno.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <signal.h>
#include <sys/wait.h>
#include <termios.h>
#include <unistd.h>
#include<dirent.h>
#include "tokenizer.h"
#include<wait.h>
#include<sched.h>

#define MAXNAMELENGTH 1024
#define MAXPROCESSNUMBER 256

/* Convenience macro to silence compiler warnings about unused function parameters. */
#define unused __attribute__((unused))

/* Whether the shell is connected to an actual terminal or not. */
bool shell_is_interactive;

/* File descriptor for the shell input */
int shell_terminal;

/* Terminal mode settings for the shell */
struct termios shell_tmodes;

/* Process group id for the shell */
pid_t shell_pgid;

int cmd_exit(struct tokens *tokens);
int cmd_help(struct tokens *tokens);
int cmd_pwd(struct tokens *tokens);
int cmd_cd(struct tokens *tokens);
int cmd_wait(struct tokens *tokens);
int cmd_fg(struct tokens *tokens);
int cmd_bg(struct tokens *tokens);

// Global
int *statusList[MAXPROCESSNUMBER];
int pidList[MAXPROCESSNUMBER];
int statusStoreList[MAXPROCESSNUMBER];
bool fgsList[MAXPROCESSNUMBER];
int processNum;

/* Built-in command functions take token array (see parse.h) and return int */
typedef int cmd_fun_t(struct tokens *tokens);

/* Built-in command struct and lookup table */
typedef struct fun_desc {
  cmd_fun_t *fun;
  char *cmd;
  char *doc;
} fun_desc_t;

fun_desc_t cmd_table[] = {
  {cmd_help, "?", "show this help menu"},
  {cmd_exit, "exit", "exit the command shell"},
  {cmd_pwd,"pwd","print out the current working directory"},
  {cmd_cd,"cd","change the current working directory"},
  {cmd_wait,"wait","Wait every subprocessed to exit, then show back promete"},
  {cmd_fg ,"fg","Move the process with id pid to the foreground."}
};

/* Prints a helpful description for the given command */
int cmd_help(unused struct tokens *tokens) {
  for (unsigned int i = 0; i < sizeof(cmd_table) / sizeof(fun_desc_t); i++)
    printf("%s - %s\n", cmd_table[i].cmd, cmd_table[i].doc);
  return 1;
}

/* Exits this shell */
int cmd_exit(unused struct tokens *tokens) {
  exit(0);
}

int cmd_pwd(unused struct tokens *tokens){
  int length=1024;
  char path[length];
  char* result=getcwd(path,length);
  if(result==NULL){
      printf ("Too lonSTDIN_FILENOg path! pwd failed...\n");
      return -1;
    }
  printf(path);
  printf("\n");
  return 0;
}
int cmd_fg(struct tokens *tokens){
  if(processNum==0) return -1;
  pid_t maingPid=getpgid(getpid());
  pid_t pid=pidList[processNum-1];
  int status;
  if(tokens_get_length (tokens)==1){
      signal(SIGTTOU,SIG_IGN);
      tcsetpgrp(STDIN_FILENO,pid);
      signal(SIGTTOU,SIG_DFL);
      kill(pid,SIGCONT);
      waitpid(pid,&status,0);
      signal(SIGTTOU,SIG_IGN);
      tcsetpgrp(STDIN_FILENO,maingPid);
      signal(SIGTTOU,SIG_DFL);
    }
  else{
      pid_t pid=atoi(tokens_get_token (tokens,1));
      for(int i=0;i<processNum;i++){
          if(pid==pidList[i]){
            signal(SIGTTOU,SIG_IGN);
            tcsetpgrp(STDIN_FILENO,pid);
            signal(SIGTTOU,SIG_DFL);
            kill(pid,SIGCONT);
            waitpid(pid,&status,0);
            signal(SIGTTOU,SIG_IGN);
            tcsetpgrp(STDIN_FILENO,maingPid);
            signal(SIGTTOU,SIG_DFL);
            }
        }
      return -1;
    }
  return 0;
}
int cmd_bg(struct tokens *tokens){
  if(processNum==0) return -1;
  if(tokens_get_length (tokens)==1){
      pid_t pid=pidList[processNum-1];
      kill(pid,SIGCONT);
    }
  else{
      pid_t pid=atoi(tokens_get_token (tokens,1));
      for(int i=0;i<processNum;i++){
          if(pidList[i]==pid){
              kill(pid,SIGCONT);
              break;
            }
        }
      return -1;
    }
  return 0;
}
int cmd_cd(struct tokens *tokens){
  if(chdir(tokens_get_token(tokens, 1))!=0){
      printf ("Change directory failed!\n");
      return -1;
    }
  return 0;
}

int cmd_wait(struct tokens *tokens){
  printf ("%d \n",processNum);
  for(int i=0;i<processNum;i++){
      int status;
      if(waitpid (-1,&status,0)==-1)
        return -1;
    }
  processNum=0;
  return 0;
}
/* Looks up the built-in command, if it exists. */
int lookup(char cmd[]) {
  for (unsigned int i = 0; i < sizeof(cmd_table) / sizeof(fun_desc_t); i++)
    if (cmd && (strcmp(cmd_table[i].cmd, cmd) == 0))
      return i;
  return -1;
}

/* Intialization procedures for this shell */
void init_shell() {
  /* Our shell is connected to standard input. */
  shell_terminal = STDIN_FILENO;

  /* Check if we are running interactively */
  shell_is_interactive = isatty(shell_terminal);
  memset(statusStoreList,-9999,MAXPROCESSNUMBER*sizeof(int));
  for(int i=0;i<MAXPROCESSNUMBER;i++)
    statusList[i]=statusStoreList+i;

  if (shell_is_interactive) {
    /* If the shell is not currently in the foreground, we must pause the shell until it becomes a
     * foreground process. We use SIGTTIN to pause the shell. When the shell gets moved to the
     * foreground, we'll receive a SIGCONT. */
    while (tcgetpgrp(shell_terminal) != (shell_pgid = getpgrp()))
      kill(-shell_pgid, SIGTTIN);

    /* Saves the shell's process id */
    shell_pgid = getpid();

    /* Take control of the terminal */
    tcsetpgrp(shell_terminal, shell_pgid);

    /* Save the current termios to a variable, so it can be restored later. */
    tcgetattr(shell_terminal, &shell_tmodes);
  }
}

bool isNameInDir(char *name,DIR * dir){
  struct dirent *de;
  while (true) {
      de=readdir(dir);
      if(de==NULL) break;
      if(strcmp(de->d_name,name)==0)
        return true;
    }
  return false;
}

void removecommold(char *pathvarcopy){
  int i=0;
  while(pathvarcopy[i]!='\0'){
      if(pathvarcopy[i]==':')
        pathvarcopy[i]='\0';
      i++;
    }
}

struct pathvarContent
{
  char *pathvarcopy;
  int beginPos;
};

bool getNextDirName(struct pathvarContent* content,char *buffer){
  if(content->pathvarcopy[content->beginPos]=='\0')
    return false;
  int length=strlen(content->pathvarcopy+content->beginPos);
  strcpy(buffer,content->pathvarcopy+content->beginPos);
  content->beginPos+=length+1;
  return true;
}

void fillArgs(char **arg,int argsNumber,struct tokens *tokens,bool *bgflag){
  for(int i=0;i<argsNumber;i++){
      arg[i]=tokens_get_token (tokens,i);
      if(strcmp(arg[i],"<")==0){
          freopen (tokens_get_token(tokens,i+1),"r",stdin);
          arg[i]=NULL;
          i++;
        }
      if(strcmp(arg[i],">")==0){
          freopen (tokens_get_token(tokens,i+1),"w",stdout);
          arg[i]=NULL;
          i++;
        }
      if(strcmp(arg[i],"&")==0){
       *bgflag=true;
       arg[i]=NULL;
        }
    }
  arg[argsNumber]=(char*)NULL;
}

void handle_sub_exit(int sig){
  //printf ("%d Doing delete process\n",processNum);
  for(int i=0;i<processNum;i++){
      if(*statusList[i]!=-9999&&WIFEXITED(*statusList[i])){
          int *tmp=statusList[i];
          memmove(*statusList+i,*statusList+1+i,processNum-i-1);
          memmove(pidList+i,pidList+1+i,processNum-i-1);
          memmove(fgsList+i,fgsList+1+i,processNum-i-1);
          statusList[processNum-1]=tmp;
          processNum--;
          i--;
        }
    }
  //printf ("%d Doing delete process\n",processNum);
}

int main(unused int argc, unused char *argv[]) {
  processNum=0;
  signal(SIGCHLD,handle_sub_exit);
  sigset_t mask;
  sigemptyset(&mask);
  sigaddset(&mask,SIGCHLD);
  pid_t mainPid=getpid();
  init_shell();
  static char line[4096];
  int line_num = 0;
  /* Please only print shell prompts when standard input is not a tty */
  if (shell_is_interactive)
    fprintf(stdout, "%d: ", line_num);
  while (fgets(line, 4096, stdin)) {
      /* Split our line into words. */
    bool processBgflag=false;
    struct tokens *tokens = tokenize(line);
    /* Find which built-in function to run. */
    char *command=tokens_get_token(tokens, 0);
    int fundex = lookup(command);
    int argsNumber=tokens_get_length(tokens);
    char **arg=(char **)malloc((argsNumber+1)*sizeof(char*));

    if (fundex >= 0) {
        cmd_table[fundex].fun(tokens);
      } else if(argsNumber!=0){
        pid_t mainPgid=getpgid(mainPid);
        fillArgs (arg,argsNumber,tokens,&processBgflag);
        pid_t pid=fork();
        pidList[processNum]=pid;
        if(pid==0){
            signal(SIGCHLD,SIG_DFL);
            pid_t subPid=getpid();
            setpgid(subPid,subPid);
            signal(SIGTTOU,SIG_IGN);
            if(!processBgflag)
                tcsetpgrp(STDIN_FILENO, subPid);
            signal(SIGTTOU,SIG_DFL);
            int errCode=execv(command,arg);
            char currentDirName[MAXNAMELENGTH];
            memset(currentDirName,0,MAXNAMELENGTH);
            struct pathvarContent contentDir;
            contentDir.beginPos=0;
            contentDir.pathvarcopy=strdup(getenv("PATH"));
            removecommold (contentDir.pathvarcopy);
            while (getNextDirName (&contentDir,currentDirName)) {
                //fprintf (stdout,"%s\n",currentDirName);
                fflush(stdout);
                DIR *dir=opendir (currentDirName);
                if(isNameInDir (command,dir)){
                    int dirNameLength=strlen(currentDirName);
                    currentDirName[dirNameLength]='/';
                    strcpy(currentDirName+dirNameLength+1,command);
                    arg[0]=currentDirName;
                    errCode=execv(currentDirName,arg);
                    printf (strerror(errno),"\n");
                    exit(errCode);
                  }
              }

            free(contentDir.pathvarcopy);
            exit(errCode);
          }
        sigprocmask(SIG_BLOCK,&mask,NULL);
        pidList[processNum]=pid;
        fgsList[processNum]=processBgflag;
        *statusList[processNum]=-9999;
        int retPid;
        if(!processBgflag){
            //printf ("%s\n %d","Catch &",processBgflag);
            retPid=waitpid (pid,statusList[processNum++],0);
            signal(SIGTTOU,SIG_IGN);
            tcsetpgrp(STDIN_FILENO,getpgid(mainPid));
            signal(SIGTTOU,SIG_DFL);
          }
        else{
          retPid=waitpid(pid,statusList[processNum++],WNOHANG);
        }
        sigprocmask(SIG_UNBLOCK,&mask,NULL);
        if(retPid==-1)
          printf ("%s\n","Something error happened!");
      }
    free(arg);
    if (shell_is_interactive)
      /* Please only print shell prompts when standard input is not a tty */
      fprintf(stdout, "%d: ", ++line_num);
    /* Clean up memory */
    tokens_destroy(tokens);
    }

  return 0;
}
