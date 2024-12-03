#include <stdio.h>
#include <string.h>
#include <stdlib.h>

#define MAX_STACK_SIZE 100
#define MAX_BLOCKS 10

// Define structures for predicates and operations
typedef struct {
    char block1;
    char block2;
} Predicate;

// Stack to hold predicates and operations
typedef struct {
    void *data[MAX_STACK_SIZE];
    int top;
} Stack;

// Global Variables
char worldState[MAX_BLOCKS][MAX_BLOCKS];  // World state
int numBlocks = 4;  // Number of blocks A, B, C, D

// Stack operations
void initStack(Stack *stack) {
    stack->top = -1;
}

int isStackEmpty(Stack *stack) {
    return stack->top == -1;
}

void push(Stack *stack, void *element) {
    if (stack->top < MAX_STACK_SIZE - 1) {
        stack->data[++stack->top] = element;
    }
}

void *pop(Stack *stack) {
    if (!isStackEmpty(stack)) {
        return stack->data[stack->top--];
    }
    return NULL;
}

void *peek(Stack *stack) {
    if (!isStackEmpty(stack)) {
        return stack->data[stack->top];
    }
    return NULL;
}

// Predicate check functions
int isOn(char block1, char block2) {
    return worldState[block1 - 'A'][block2 - 'A'];
}

int isClear(char block) {
    for (int i = 0; i < numBlocks; i++) {
        if (worldState[i][block - 'A']) {
            return 0;
        }
    }
    return 1;
}

int isArmEmpty = 1;
char holdingBlock = '\0';

// Goal Stack Planner Functions
void applyStackOperation(char block1, char block2) {
    printf("STACK(%c, %c)\n", block1, block2);
    worldState[block1 - 'A'][block2 - 'A'] = 1;  // Block1 is on Block2
    isArmEmpty = 1;
    holdingBlock = '\0';
}

void applyUnstackOperation(char block1, char block2) {
    printf("UNSTACK(%c, %c)\n", block1, block2);
    worldState[block1 - 'A'][block2 - 'A'] = 0;  // Block1 is no longer on Block2
    isArmEmpty = 0;
    holdingBlock = block1;
}

void applyPickupOperation(char block) {
    printf("PICKUP(%c)\n", block);
    isArmEmpty = 0;
    holdingBlock = block;
}

void applyPutdownOperation(char block) {
    printf("PUTDOWN(%c)\n", block);
    isArmEmpty = 1;
    holdingBlock = '\0';
}

// Plan Steps to achieve goal
void planSteps(Stack *stack) {
    while (!isStackEmpty(stack)) {
        Predicate *goal = (Predicate *)pop(stack);

        // Check if the goal is satisfied in the current world state
        if (isOn(goal->block1, goal->block2)) {
            continue;
        }

        // Get the operation to satisfy the goal
        if (isClear(goal->block2) && holdingBlock == goal->block1) {
            applyStackOperation(goal->block1, goal->block2);
        } else if (isOn(goal->block1, goal->block2)) {
            applyUnstackOperation(goal->block1, goal->block2);
        } else if (isArmEmpty && isClear(goal->block1)) {
            applyPickupOperation(goal->block1);
        } else {
            applyPutdownOperation(goal->block1);
        }
    }
}

// Function to set the initial state from user input
void setInitialState(int numBlocks) {
    int numPairs;
    printf("Enter the number of ON pairs for the start state: ");
    scanf("%d", &numPairs);

    for (int i = 0; i < numPairs; i++) {
        char block1, block2;
        printf("Enter ON(%c, %c): ", block1, block2);
        scanf(" %c %c", &block1, &block2);
        worldState[block1 - 'A'][block2 - 'A'] = 1;
    }
}

// Function to input and set goal state
void inputGoalState(Stack *stack) {
    int numGoals;
    printf("Enter the number of ON goals: ");
    scanf("%d", &numGoals);

    for (int i = 0; i < numGoals; i++) {
        char block1, block2;
        printf("Enter goal ON(%c, %c): ", block1, block2);
        scanf(" %c %c", &block1, &block2);
        Predicate *goal = (Predicate *)malloc(sizeof(Predicate));
        goal->block1 = block1;
        goal->block2 = block2;
        push(stack, goal);
    }
}

// Main Function
int main() {
    // Initialize world state
    memset(worldState, 0, sizeof(worldState));

    // Get number of blocks
    printf("Enter the number of blocks: ");
    scanf("%d", &numBlocks);

    // Set initial state
    setInitialState(numBlocks);

    // Stack initialization
    Stack stack;
    initStack(&stack);

    // Input goal state
    inputGoalState(&stack);

    // Plan steps to reach the goal state
    printf("\nPlanning steps to reach the goal state:\n");
    planSteps(&stack);

    return 0;
}
