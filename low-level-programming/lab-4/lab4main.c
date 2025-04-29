#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "linked_list.h"

int main(){
    char *line = NULL;
    size_t size;
    int len;
    struct LinkedList list;
    int index;
    int value;
    const char delimiter[2] = " ";
    char *token;
    char *ptr;
    int ret;
    init_list(&list);



    while(1){
        printf("Please enter your command (use help if you don't remember):");
        len = getline(&line, &size, stdin);
        if(len <= 0) continue;
        /* Remove the last \n */
        line[len-1] = '\0';
        token = strtok(line, delimiter);
        if (strcmp(token, "add") == 0) {
            token = strtok(NULL, delimiter);
            if (token == NULL) {
                printf("Error: List index and node value must follow this command.");
            }
            else {
                ret = strtol(token, &ptr, 10);
                if (ptr == token) {
                    printf("Error: List index must follow this command.");
                }
                else if(ret < 0) {
                    printf("Error: List index must be greater than or equal to zero.");
                }
                else {
                    index = ret;
                    token = strtok(NULL, delimiter);
                    if (token == NULL) {
                        printf("Error: Node value must follow the list index.");
                    }
                    else {
                        ret = strtol(token, &ptr, 10);
                        if (ptr == token) {
                            printf("Error: Node value must follow the list index.");
                        }
                        else {
                            value = ret;
                            token = strtok(NULL, delimiter);
                            if (token != NULL) {
                                printf("Error: Too many arguments were inputted for this command.");
                            }
                            else {
                                insert_node(&list, index, value);
                            }
                        }
                    }
                }
            }
        }

        else if(strcmp(token, "delete") == 0) {
            token = strtok(NULL, delimiter);
            if (token == NULL) {
                printf("Error: List index must follow this command.");
            }
            else {
                ret = strtol(token, &ptr, 10);
                if (ptr == token) {
                    printf("Error: List index must follow this command.");
                }
                else if(ret < 0) {
                    printf("Error: List index must be greater than or equal to zero.");
                }
                else {
                    index = ret;
                    token = strtok(NULL, delimiter);
                    if (token != NULL) {
                        printf("Error: Too many arguments were inputted for this command.");
                    }
                    else {
                        remove_node(&list, index); 
                    }
                }
            }
        }

        else if(strcmp(line, "exit") == 0){
            printf("Bye\n");
            break;
        }
        else if(strcmp(line, "help") == 0){
            printf("exit: quits this tool\n");
            printf("help: print all commands\n");
            printf("print: print all values in the linked list\n");
            printf("add <i> <value>: add value as the ith element\n");
            printf("delete <i>: delete the ith element\n");
        }
        else if(strcmp(line, "print") == 0){
            print_list(&list);
        }
        else {
            printf("Error: The command you entered is not a valid command.");
        }
    }
/*    destroy_list(&list); */

}
