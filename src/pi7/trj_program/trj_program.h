#ifndef __trj_program_h
#define __trj_program_h
#define MAX_PROGRAM_LINES 28


typedef struct {
	int x;
	int y;
} tpr_Data;

extern int tpr_storeProgram(char* program_bytes);
extern tpr_Data tpr_getLine(int line);
extern void tpr_init();
#endif
