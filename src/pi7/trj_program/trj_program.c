/*
 * Modulo: Programa Trajetoria
 * Armazena o programa da trajetoria a ser executada
 */

// max NC program size

#include "trj_program.h"
#include "../command_interpreter/command_interpreter.h"

#include <stdlib.h>
#include <string.h>
#include <stdio.h>

// structure to store NC program
tpr_Data tpr_program[MAX_PROGRAM_LINES];

int tpr_storeProgram(char* texto) {

	int i=1, val[2];
	char* separa = strtok(texto, "-");

	while (separa != NULL) {
		val[(i-1)%2]=(int)atof(separa);
		if (i%2==0) {
		tpr_program[i/2].x = val[0];
		tpr_program[i/2].y = val[1];	
		// printf("\n%d",val[0]);
		// printf("\n%d\n",val[1]);
		}
		i++;
		separa = strtok(NULL, "-");
	}
	return 1;
} // tpr_storeProgram

tpr_Data tpr_getLine(int line) {
	return tpr_program[line];
} // tpr_getLine

void tpr_init() {
	
    for (int i=0; i<MAX_PROGRAM_LINES;i++) {
  	  tpr_program[i].x = 0;
  	  tpr_program[i].y = 420;  
    }

	// tpr_program[0].x = 51;
	// tpr_program[0].y = 305;

//    tpr_program[MAX_PROGRAM_LINES-1].x=13;
//    tpr_program[MAX_PROGRAM_LINES-1].y=298;

//    tpr_program[MAX_PROGRAM_LINES].x=51;
//    tpr_program[MAX_PROGRAM_LINES].x=305;

} //tpr_init
