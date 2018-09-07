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


const static int MAXNAMELENGTH=1024;
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
  {cmd_cd,"cd","change the current working directory"}
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
      printf ("Too long path! pwd failed...\n");
      return -1;
    }
  printf(path);
  printf("\n");
  return 0;
}

int cmd_cd(struct tokens *tokens){
  if(chdir(tokens_get_token(tokens, 1))!=0){
      printf ("Change directory failed!\n");
      return -1;
    }
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

int main(unused int argc, unused char *argv[]) {
  init_shell();

  static char line[4096];
  int line_num = 0;

  /* Please only print shell prompts when standard input is not a tty */
  if (shell_is_interactive)
    fprintf(stdout, "%d: ", line_num);

  while (fgets(line, 4096, stdin)) {
    /* Split our line into words. */
    struct tokens *tokens = tokenize(line);

    /* Find which built-in function to run. */
    char *command=tokens_get_token(tokens, 0);
    int fundex = lookup(command);

    if (fundex >= 0) {
      cmd_table[fundex].fun(tokens);
    } else {
      pid_t pid=fork();
      if(pid==0){
          int argsNumber=tokens_get_length(tokens);
          char **arg=(char **)malloc((argsNumber+1)*sizeof(char*));
          for(int i=0;i<argsNumber;i++){
              arg[i]=tokens_get_token (tokens,i);
            }
          arg[argsNumber]=(char*)NULL;
          int errCode=execv(command,arg);
          //printf (strerror(errno),"\n");


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
      int retCode;
      int retPid=waitpid (-1,&retCode,0);
      if(!WIFEXITED(retCode))
        fprintf(stdout, "This shell doesn't know how to run programs.\n");
    }

    if (shell_is_interactive)
      /* Please only print shell prompts when standard input is not a tty */
      fprintf(stdout, "%d: ", ++line_num);

    /* Clean up memory */
    tokens_destroy(tokens);
  }

  return 0;
}
