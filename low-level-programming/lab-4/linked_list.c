#include <stdio.h>
#include <stdlib.h>
#include "linked_list.h"

void init_list(struct LinkedList *list){
    list->head = NULL;
    list->tail = NULL;
}

void insert_node(struct LinkedList *list, int index, int value){
    struct ListNode* node;
    struct ListNode *tempPtr;
    int counter;
    node = (struct ListNode*)malloc(sizeof(struct ListNode));
    /* If inserting node into empty list */
    if (list->head == NULL && list->tail == NULL) {
        list->tail = node;
        list->head = node;
        node->data = value;
        node->prev = NULL;
        node->next = NULL;
    }

    /* Finding address of node of index and storing address in temporary pointer */
    tempPtr = list->head;
    counter = 0;
    while(counter < index && tempPtr->next != NULL) {
        tempPtr = tempPtr->next;
        counter++;
    }

    /* If inserting a node at the beginning of a non-empty list */
    if (index == 0) {
        node->data = value;
        node->next = list->head;
        node->prev = NULL;
        list->head->prev = node;
        list->head = node;
    }

    /* If inserting a node at the end of a non-empty list */
    else if(tempPtr == list->tail) {
        node->data = value;
        node->next = NULL;
        node->prev = list->tail;
        list->tail->next = node;
        list->tail = node;
    }

    /* If inserting a node in middle of non-empty list */
    else if(tempPtr != NULL) {
        node->data = value;
        node->next = tempPtr->next;
        node->prev = tempPtr;
        if (tempPtr->next != NULL) {
            tempPtr->next->prev = node;
        }
        tempPtr->next = node;
    }

    else {
        printf("Error: Invalid index.");
    }
}

void remove_node(struct LinkedList *list, int index){
    struct ListNode *currNode;
    struct ListNode *nodeToDelete;
    int i;
    currNode = list->head;
    for (i = 1; i < index + 1 && currNode != NULL; i++) {
        currNode = currNode->next;
    }

    /* If node to be deleted is the first node */
    if (index == 0) {
        nodeToDelete = list->head;
        list->head = list->head->next;
        list->head->prev = NULL;
        free(nodeToDelete);
    }

    /* If node to be deleted is the last node */
    else if(currNode == list->tail) {
        nodeToDelete = list->tail;
        list->tail = list->tail->prev;
        list->tail->next = NULL;
        free(nodeToDelete);
    }

    /* If node to be deleted is not the first or last node */
    else if(currNode != NULL) {
        currNode->prev->next = currNode->next;
        currNode->next->prev = currNode->prev;
        free(currNode);
    }

    else {
        printf("Error: Invalid index.");
    }
}

void destroy_list(struct LinkedList *list){

}

void print_list(struct LinkedList *list){
    struct ListNode* node;
    node = list->head;
    while (node != NULL) {
        if (node->next == NULL) {
            printf("%d ", node->data);
        }
        else {
            printf("%d->", node->data);
        }
        node = node->next;
    }
}
