#include <stdlib.h>
#include <unistd.h>
#include <stdio.h>
#include <string.h>
#include <sys/wait.h>
#include <sys/stat.h>
#include <fcntl.h>

struct userInput {
  // struct for a single cmd and its arguments
  char* cmd; 
  char** args; 
  int args_num; 
  int has_redirection; 
}; 

struct listUserInputs {
  // struct for a list of cmd and its arguments
  struct userInput* inputs; 
  int inputs_num; 
}; 

void myPrint(char *msg) {
  // prints message to shell 
  write(STDOUT_FILENO, msg, strlen(msg));
}

void printError() {
  // prints the one and only error message
  char error_message[30] = "An error has occurred\n";
  write(STDOUT_FILENO, error_message, strlen(error_message));
}
 
//----------------------- SEMICOLON AND WHITESPACE -----------------------------

void removeRepeatWhitespace(char* pinput) {
  /*
  Removes white spaces before first char and after last char. Also 
  removes any repeating white spaces between two strings

  Inputs: 
    char* pinput: the user input string
  */

  int i = 0, j = 0;
  int whitespaceFound = 0;

  while (pinput[i] == ' ' || pinput[i] == '\t') {
    i++;
  }

  while (pinput[i]) {
    if (pinput[i] == ' ' || pinput[i] == '\t') {
      whitespaceFound = 1;
    } 
    else {
      if (whitespaceFound && j > 0) {
        pinput[j] = ' ';
        j++; 
      }
      pinput[j] = pinput[i];
      j++; 
      whitespaceFound = 0;
    }
    i++;
  }
  
  if (j > 0 && pinput[j - 1] == ' ') {
    j--;
  } 
  pinput[j] = '\0';
}

int semicolonNum(char *pinput) {
  /*
  Calculates the number of semicolons in the user inputs

  Inputs: 
    char* pinput: the user input string 

  Returns: 
    int len: the number of semicolons
  */

  int i = 0; int len = 0; 
  while (pinput[i]) {
    if (pinput[i] == ';') {
      len++;
    }
    i++; 
  }
  len++; 
  return len; 
}

void adjustSemicolon(char* pinput) {
  /*
  Adds whitespace between a semicolon and the next word if no whitespace exists
  Adds whitespace between a semicolon and the word before if no whitespace exists
  Ensures a semicolon at the end of the string if one doesn't already exist

  Inputs: 
    char* pinput: the user input string
  */

  int i = 0, j = 0;
  int len = strlen(pinput);
  int cmdNum = semicolonNum(pinput); 
  int needsTrailingSemicolon = 0; 

  if (len > 0 && pinput[len - 1] != ';') {
    needsTrailingSemicolon = 1;
  }

  int extraSpace = 2 * cmdNum; 
  if (needsTrailingSemicolon) {
    extraSpace += 1; 
  }
  
  char *result = (char *)malloc(len + extraSpace + 1);
  if (result == NULL) {
    printError(); 
    return;
  }

  for (i = 0; i < len; i++) {
    if (pinput[i] == ';') {
      if (j > 0 && result[j - 1] != ' ') {
        result[j++] = ' ';
      }
      result[j++] = ';';

      if ((i + 1 < len) && pinput[i + 1] != ' ' && pinput[i + 1] != '\0') {
        result[j] = ' ';
        j++; 
      }
    } 
    else {
      result[j] = pinput[i];
      j++; 
    }
  }

  if (needsTrailingSemicolon) {
    result[j] = ';';
    j++; 
  }

  result[j] = '\0'; 

  strcpy(pinput, result);
  free(result);
}

void adjustRedirection(char* pinput) {
  /*
  Adds whitespace between > or +> and the next word if no whitespace exists
  Adds whitespace between > or +> and the word before if no whitespace exists

  Inputs: 
    char* pinput: the user input string
  */
  
  int i = 0, j = 0;
  int len = strlen(pinput);
  char *result = (char *)malloc(2 * len + 1); // Allocate enough space
  if (result == NULL) {
    printError(); 
  }

  for (i = 0; i < len; i++) {
    if (pinput[i] == '>') {
      if (j > 0 && result[j - 1] != ' ') {
        result[j] = ' ';
        j++; 
      }
      result[j] = '>';
      j++; 

      if (i + 1 < len && pinput[i + 1] == '+') {
        result[j] = '+';
        j++; 
        i++; 
      }

      if (i + 1 < len && pinput[i + 1] != ' ') {
        result[j] = ' ';
        j++; 
      }
    } 
    else {
      result[j] = pinput[i];
      j++; 
    }
  }

  result[j] = '\0';

  strcpy(pinput, result);
  free(result);
}

int countWords(char* phrase) {
  /*
  Counts the number of words in the phrase 

  Input: 
    char* phrase: the phrase
  */
  int count = 0;
  int inWord = 0;

  if (phrase == NULL || phrase[0] == '\0') {
    return 0;  // handles empty or NULL input
  }

  int i = 0; 
  while (phrase[i]) {
    if (phrase[i] == ' ' || phrase[i] == '\t' || phrase[i] == '\n') {
      inWord = 0;  
    } 
    else if (inWord == 0) {
      inWord = 1;  
      count++;    
    }
    i++; 
  }

  return count;
}

//-------------------------- STRUCT INPUTS -------------------------------------

int cmdLen(char* pinput) {
  /*
  Calculates the length of the command which is the first string at the beginning
  of the input or after a semicolon 

  Inputs: 
    char* pinput: the user input string 

  Returns: 
    int len: the length of the cmd
  */

  int i = 0; int len = 0; 
  while (pinput[i] && pinput[i] != ' ') {
    len++; 
    i++; 
  }
  len++; 

  return len; 
}

int isOnlyWhitespace(char* pinput) {
  /*
  Calculates whether the string only contains whitespace

  Inputs: 
    char* pinput: the user input string 

  Returns: 
    int result: false for nonwhitespace character or null, true otherwise
  */

  if (pinput == NULL) {
    return 0;
  }

  int i = 0; 
  while (pinput[i]) {
    if (pinput[i] != ' ' && pinput[i] != '\t' && pinput[i] != '\n' && 
      pinput[i] != '\r' && pinput[i] != '\v' && pinput[i] != '\f') {
        return 0; 
    }
    i++;
  }
  return 1;
}

void freeInputs(struct listUserInputs *result) {
  /*
  Frees the memory of the listUserInputs strict

  Inputs: 
    char* result: the struct
  */

  for (int i = 0; i < result->inputs_num; i++) {
      free(result->inputs[i].cmd);
      for (int j = 0; j < result->inputs[i].args_num; j++) {
          free(result->inputs[i].args[j]);
      }
      free(result->inputs[i].args);
  }

  free(result->inputs);
  free(result);
}

struct listUserInputs *createUserInput(char* pinput) {    
  /*
  Creates a listUserInput struct using the inputs from pinput

  Inputs:
    char* pinput: the input

  Returns: 
    struct listUserInputs: the struct
  */

  int cmdNum = semicolonNum(pinput); 

  struct listUserInputs *result = (struct listUserInputs *)malloc(sizeof(struct listUserInputs));
  if (result == NULL) {
    printError(); 
    return NULL; 
  }

  result->inputs = (struct userInput *)malloc(sizeof(struct userInput) * cmdNum);
  if (result->inputs == NULL) {
    printError(); 
    return NULL; 
  }

  // creates the struct userInput for each cmd and its arguments
  const char semicolon[2] = ";";
  const char whitespace[2] = " ";
  int ui = 0; int phraseNum = 0; 
  char** phrases; 

  char *pinputCopy = (char *)malloc(strlen(pinput) + 1);
  if (pinputCopy == NULL) {
    printError(); 
    return NULL; 
  }
  strcpy(pinputCopy, pinput); 

  char *phrase;
  char *word; 

  //---------------- FOR MULTI COMMANDS ----------------------------------------

  phrase = strtok(pinputCopy, semicolon); 

  while (phrase != NULL) {
    result->inputs[ui].args_num = countWords(phrase); 

    result->inputs[ui].args = (char**)malloc((result->inputs[ui].args_num + 1)* sizeof(char*));
    if (result->inputs[ui].args == NULL) {
      printError();
      return NULL; 
    }
    phraseNum++; 
    ui++; 
    phrase = strtok(NULL, semicolon); 
  }  

  phrases = (char **)malloc(phraseNum * sizeof(char*)); 
  if (phrases == NULL) {
    printError();
    return NULL; 
  }

  strcpy(pinputCopy, pinput); 
  phrase = strtok(pinputCopy, semicolon); 
  int k = 0; 
  while (phrase != NULL) {
    phrases[k] = (char*)malloc((strlen(phrase) + 1) * sizeof(char)); 
    if (phrases[k] == NULL) {
      printError();
      return NULL; 
    }
    strcpy(phrases[k], phrase); 
    k++; 
    phrase = strtok(NULL, semicolon); 
  }  

  //------------------- FOR INDIVIDUAL COMMANDS --------------------------------
  
  for (int ui = 0; ui < phraseNum; ui++) {
    int isCmd = 1; int j = 0; 
    result->inputs[ui].has_redirection = 0; 
    char *phraseCopy = (char *)malloc(strlen(phrases[ui]) + 1);
      if (phraseCopy == NULL) {
        printError();
        return NULL; 
      }
    strcpy(phraseCopy, phrases[ui]);

    // handles whitespace command
    if (isOnlyWhitespace(phraseCopy)) {
      result->inputs[ui].cmd = (char *)malloc((strlen(phraseCopy) + 1) * sizeof(char)); 
        if (result->inputs[ui].cmd== NULL) {
          printError();
          return NULL; 
        }
      strcpy(result->inputs[ui].cmd, " "); 

      result->inputs[ui].args[j] = (char*)malloc((strlen(phraseCopy) + 1) * sizeof(char));
      if (result->inputs[ui].args[j] == NULL) {
        printError();
        return NULL; 
      }
      strcpy(result->inputs[ui].args[j], " "); 

      j++; 
    }

    word = strtok(phraseCopy, whitespace); 

    while (word != NULL) {
      if (isCmd) {
        result->inputs[ui].cmd = (char *)malloc((strlen(word) + 1) * sizeof(char)); 
        if (result->inputs[ui].cmd == NULL) {
          printError();
          return NULL; 
        }

        isCmd = 0;
        strcpy(result->inputs[ui].cmd, word); 
      }
      
      result->inputs[ui].args[j] = (char*)malloc((strlen(word) + 1) * sizeof(char));
      if (result->inputs[ui].args[j] == NULL) {
        printError();
        return NULL; 
      }

      if (isCmd == 0) {
        if (strcmp(word, ">") == 0 || strcmp(word, ">+") == 0) {
          result->inputs[ui].has_redirection = 1; 
        }
      }
      
      strcpy(result->inputs[ui].args[j], word); 
      j++; 
      
      word = strtok(NULL, whitespace); 
    }
    result->inputs[ui].args[j] = NULL; 
    free(phraseCopy); 
  }
  
  result->inputs_num = phraseNum; 
  free(pinputCopy);

  return result; 
}

//---------------------------- COMMAND LOGIC -----------------------------------

int isDirectory(char* path) {
  /*
  Checks if the given string is a directory path or a file format

  Inputs: 
    char* path: the string

  Returns: 
    int: True (1) for if it is a folder regardless of if the folder exists or not, 
        and False (0) for if it is a file regardless of if the file exists or not
  */
  int i = 0; 
  while (path[i]) {
    if (path[i] == '/') {
      return 1; 
    }
    i++; 
  }

  return 0;
}

void splitPath(char* input, char* directory, char* filename) {
  /*
  Given a string, separates it by the last backslash to split the directories with
  the file

  Inputs: 
    char* input: the entire path string 
    char* directory: returns the directory part of the string
    char* filename: returns the file part of the stirng
  */
  char *lastSlash = strrchr(input, '/');

  if (lastSlash != NULL) {
    int i = lastSlash - input;
    strncpy(directory, input, i);
    directory[i] = '\0';

    strcpy(filename, lastSlash + 1);
  } 
  else {
    directory[0] = '\0'; 
    strcpy(filename, input);
  }
}

int inputFiles(struct listUserInputs* input, int i) {
  /*
  Assuming the cmd is cat, returns the number of input files to a redirection command 

  Inputs: 
    struct listUserInputs* input: the input struct 
    int i: the input index

  Returns: 
    int num: number of input files 
  */

  int num = 0; 
  for (int j = 1; j < input->inputs[i].args_num; j++) {
    if (strcmp(input->inputs[i].args[j], ">") == 0 || 
        (strcmp(input->inputs[i].args[j], ">+") == 0)) {
      break; 
    }
    num++; 
  }

  return num; 
}

void redirectionCmd(struct listUserInputs* input, int i) {
  /*
  Handles both advanced and normal redirection 

  Inputs: 
    struct listUserInputs* input: the input struct 
    int i: the input index
  */
  int j = 1; int k = 0; 
  int inFolder = 0; char prevDir[514]; char cwd[514]; 
  if (strcmp(input->inputs[i].cmd, ">") == 0 || (strcmp(input->inputs[i].cmd, ">+") == 0)) {
    printError(); 
  }
  else {
    for (j = 1; j < input->inputs[i].args_num; j++) {

    //------------------- ADVANCED REDIRECTION ---------------------------------
      if (strcmp(input->inputs[i].args[j], ">+") == 0) {
        if (j != input->inputs[i].args_num - 2) {
          printError(); 
          break; 
        }
        else {
          if (isDirectory(input->inputs[i].args[j + 1]) == 1) {
            char tempDir[strlen(input->inputs[i].args[j + 1])];
            char tempFile[strlen(input->inputs[i].args[j + 1])];
            splitPath(input->inputs[i].args[j + 1], tempDir, tempFile); 

            char* value = getenv(tempDir); 
            if (value == NULL) {
              printError();
              break; 
            }
            else {
              if (getcwd(cwd, sizeof(cwd)) == NULL) {
                printError(); 
                break; 
              }
              strcpy(prevDir, cwd);

              if (chdir(tempDir) != 0) {
                printError(); 
                break; 
              }

              inFolder = 1; 
            }
          }
          
          int original_fd = open(input->inputs[i].args[j + 1], O_RDWR);

          // behave like normal redirection
          if (original_fd < 0) {
            original_fd = creat(input->inputs[i].args[j + 1], S_IRWXU | S_IRWXG | S_IRWXO); 
            if (original_fd < 0) {
              printError(); 
              break; 
            }
            dup2(original_fd, STDOUT_FILENO); 

            char** outputCmd = (char**)malloc((j) * sizeof(char*));
            if (outputCmd == NULL) {
              printError(); 
            }
            for (k = 0; k < j; k++) {
              outputCmd[k] = (char*)malloc(
                (strlen(input->inputs[i].args[k]) + 1) * sizeof(char));
              strcpy(outputCmd[k], input->inputs[i].args[k]); 
            }
          
            outputCmd[k] = NULL; 
              
            int status_code = execvp(outputCmd[0], outputCmd);
            if (status_code == -1) {
              close(original_fd);
              printError(); 
              break; 
            }

            for (k = 0; k < j; k++) {
              free(outputCmd[k]); 
            }
            free(outputCmd); 
          }

          // adds to front
          else {
            pid_t pid = fork(); 
            int status; 
            
            if (pid == 0) {
              // Child
              int temp_fd = creat("temp.txt", S_IRWXU | S_IRWXG | S_IRWXO); 
              if (temp_fd < 0) {
                printError(); 
                break; 
              }
              if (close(temp_fd) < 0) {
                printError(); 
                break;
              }

              temp_fd = open("temp.txt", O_APPEND | O_WRONLY);
              if (temp_fd < 0) {
                printError(); 
                break;
              }

              dup2(temp_fd, STDOUT_FILENO); 
              close(temp_fd);

              char** outputCmd = (char**)malloc((j) * sizeof(char*));
              if (outputCmd == NULL) {
                printError(); 
              }
              for (k = 0; k < j; k++) {
                outputCmd[k] = (char*)malloc(
                  (strlen(input->inputs[i].args[k]) + 1) * sizeof(char));
                strcpy(outputCmd[k], input->inputs[i].args[k]); 
              }
            
              outputCmd[k] = NULL; 
                
              int status_code = execvp(outputCmd[0], outputCmd);
              if (status_code == -1) {
                printError(); 
                break; 
              }

              for (k = 0; k < j; k++) {
                free(outputCmd[k]); 
              }
              free(outputCmd); 

              exit(0); 
            }

            else {
              // Parent
              if (waitpid(pid, &status, 0) == -1) {
                printError(); 
                break; 
              }

              int temp_fd = open("temp.txt", O_WRONLY | O_APPEND);
              if (temp_fd < 0) {
                printError();
                exit(0);
              }

              // adds from original_fd to temp_fd
              char* buffer = (char*)malloc(514 * sizeof(char)); 

              int original_read = read(original_fd, buffer, sizeof(buffer));
              while (original_read > 0) {
                int original_write = write(temp_fd, buffer, original_read);
                if (original_write < 0) {
                  printError(); 
                  close(temp_fd); 
                  close(original_fd);
                  break; 
                }
                (original_read = read(original_fd, buffer, sizeof(buffer)));
              }

              original_read = read(temp_fd, buffer, sizeof(buffer));
              while (original_read > 0) {
                int original_write = write(original_fd, buffer, original_read);
                if (original_write < 0) {
                  printError();
                  close(temp_fd);  
                  close(original_fd);
                  break; 
                }
                (original_read = read(temp_fd, buffer, sizeof(buffer)));
              }

              close(temp_fd);
              close(original_fd);

              // write back to the original file
              temp_fd = open("temp.txt", O_RDONLY);
              if (temp_fd < 0) {
                printError();
                exit(0); 
              }

              original_fd = open(input->inputs[i].args[j + 1], O_WRONLY | O_TRUNC);
              if (original_fd < 0) {
                printError();
                close(temp_fd);
                exit(0);
              }

              original_read = read(temp_fd, buffer, sizeof(buffer));
              while (original_read > 0) {
                int original_write = write(original_fd, buffer, original_read);
                if (original_write < 0) {
                  printError();
                  close(temp_fd);
                  close(original_fd);
                  break;
                }
                original_read = read(temp_fd, buffer, sizeof(buffer));
              }

              close(temp_fd);
              remove("temp.txt"); 
            }
          }

          if (inFolder == 1) {
            if (chdir(prevDir) != 0) {
              printError(); 
              close(original_fd); 
              break; 
            }
          }

          if (close(original_fd) < 0) {
            printError(); 
            break; 
          }
        }
      }

      //------------------- SIMPLE REDIRECTION -----------------------------------
      else if (strcmp(input->inputs[i].args[j], ">") == 0) {
        if (j != input->inputs[i].args_num - 2) {
          printError(); 
          break; 
        }
        else {
          if (isDirectory(input->inputs[i].args[j + 1]) == 1) {
            char tempDir[strlen(input->inputs[i].args[j + 1])];
            char tempFile[strlen(input->inputs[i].args[j + 1])];
            splitPath(input->inputs[i].args[j + 1], tempDir, tempFile); 

            char* value = getenv(tempDir); 
            if (value == NULL) {
              printError();
              break; 
            }
            else {
              if (getcwd(cwd, sizeof(cwd)) == NULL) {
                printError(); 
                break; 
              }
              strcpy(prevDir, cwd);

              if (chdir(tempDir) != 0) {
                printError(); 
                break; 
              }

              inFolder = 1; 
            }
          }

          int fd = open(input->inputs[i].args[j + 1], O_WRONLY);
          if (fd < 0) {
            fd = creat(input->inputs[i].args[j + 1], S_IRWXU | S_IRWXG | S_IRWXO); 
            dup2(fd, STDOUT_FILENO); 

            char** outputCmd = (char**)malloc((j) * sizeof(char*));
            if (outputCmd == NULL) {
              printError(); 
              close(fd); 
              break; 
            }
            for (k = 0; k < j; k++) {
              outputCmd[k] = (char*)malloc(
                (strlen(input->inputs[i].args[k]) + 1) * sizeof(char));
              strcpy(outputCmd[k], input->inputs[i].args[k]); 
            }
          
            outputCmd[k] = NULL; 
              
            int status_code = execvp(outputCmd[0], outputCmd);
            if (status_code == -1) {
              printError(); 
              close(fd); 
              break; 
            }

            for (k = 0; k < j; k++) {
              free(outputCmd[k]); 
            }
            free(outputCmd); 
          }

          else {
            printError(); 
            break; 
          }

          if (inFolder == 1) {
            if (chdir(prevDir) != 0) {
              printError(); 
              close(fd);
              break; 
            }
          }

          if (close(fd) < 0) {
            printError(); 
            break; 
          }
        }
      }
    }
  }
}


void commandLogic(char* pinput) {
  /*
  Determines which commands to run for the entire input 

  Inputs:
    char* pinput: the input
  */

  pinput[strlen(pinput) - 1] = '\0';
  removeRepeatWhitespace(pinput); 
  adjustRedirection(pinput); 
  adjustSemicolon(pinput); 

  struct listUserInputs *input = createUserInput(pinput); 

  for (int i = 0; i < input->inputs_num; i++) {
    if (strcmp(input->inputs[i].cmd, " ") == 0) {
      continue; 
    }

    else if (strcmp(input->inputs[i].cmd, "pwd") == 0) {
      if (input->inputs[i].args_num == 1) {
        char cwd[514]; 
        myPrint(getcwd(cwd, sizeof(cwd))); 
        myPrint("\n"); 
      }
      else {
        printError(); 
        continue; 
      }
    }
    else if (strcmp(input->inputs[i].cmd, "cd") == 0) {
      if (input->inputs[i].args_num == 1) {
        chdir(getenv("HOME")); 
      }
    
      else if (input->inputs[i].args_num == 2) {
        if (chdir(input->inputs[i].args[1]) != 0) {
          printError(); 
          continue; 
        }
      }
      
      else {
        printError(); 
        continue;  
      }
    }
    else if (strcmp(input->inputs[i].cmd, "exit") == 0) {
      if (input->inputs[i].args_num == 1) {
        exit(0);
      }
      else {
        printError(); 
        continue; 
      }
    }
  
    else {
      pid_t pid = fork(); 
      int status; 
      
      if (pid == 0) {
        // Child
        // redirection commands
        if (input->inputs[i].has_redirection == 1) {
          redirectionCmd(input, i); 
          exit(0); 
        }

        // no redirection commands
        else {
          int status_code = execvp(input->inputs[i].cmd, input->inputs[i].args);
          if (status_code == -1) {
            printError(); 
            exit(0); 
          }
        }
      }
      else {
        // Parent
        if (waitpid(pid, &status, 0) == -1) {
          printError(); 
          continue; 
        }
      }
    }
  }
  
  freeInputs(input); 
}

//--------------------------- MAIN ---------------------------------------------

int main(int argc, char *argv[]) 
{
  size_t buff_size = 514; 
  char cmd_buff[buff_size];
  char *full_cmd;  
  size_t full_cmd_size = 0;  
  char *pinput;

  if (argc == 1) {
    while (1) {    
      myPrint("myshell> ");
      pinput = fgets(cmd_buff, sizeof(cmd_buff), stdin);
      if (!pinput) {
        exit(0);
      }
  
      commandLogic(pinput);     
    }
  }

  else {
    for (int i = 1; i < argc; i++) {
      FILE* file = fopen(argv[i], "r");
      if (file == NULL) {
        printError(); 
        return 1;
      }

      while (fgets(cmd_buff, sizeof(cmd_buff), file) != NULL) {
        // handles buffer overflow
        size_t buff_len = strlen(cmd_buff);

        if (buff_len >= buff_size - 1 && cmd_buff[buff_len - 1] != '\n') {
          full_cmd_size = buff_len + 1;
          full_cmd = malloc(full_cmd_size);
          if (full_cmd == NULL) {
            printError();
            fclose(file);
            return 0;
          }

          strcpy(full_cmd, cmd_buff);

          int character;
          while ((character = fgetc(file)) != '\n' && character != EOF) {
            size_t new_size = full_cmd_size + 1;
            char *temp = realloc(full_cmd, new_size);
            if (temp == NULL) {
              free(full_cmd);
              printError();
              fclose(file);
              return 0;
            }
            full_cmd = temp;
            full_cmd[full_cmd_size - 1] = character;
            full_cmd_size++;
          }

          full_cmd[full_cmd_size - 1] = '\0'; 
          myPrint(full_cmd);
          myPrint("\n");
          printError();

          free(full_cmd);
          full_cmd = NULL;
          full_cmd_size = 0;
          continue;
        }

        // handles empty line
        if (isOnlyWhitespace(cmd_buff)) {
          continue; 
        }
        
        // handles commands
        myPrint(cmd_buff); 
        commandLogic(cmd_buff); 

      }
      fclose(file);
      return 0;
    }
  }

  
}
