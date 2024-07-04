/**
 * Modulo: Comunicacao MODBUS (simplificada)
 * Usa a Serial0 para comunicar-se
 * [jo:230927] usa UART0 e UART1 para comunicação
 */

/*
 * FreeRTOS includes
 */
//#include "FreeRTOS.h"
//#include "queue.h"
#include <stdbool.h>
#include <stdio.h>

// Drivers for UART, LED and Console(debug)
//#include <cr_section_macros.h>
//#include <NXP/crp.h>
//#include "LPC17xx.h"
//#include "type.h"
#include "drivers/uart/uart.h"
//#include "hardware/uart.h"

// Header files for PI7
#include "comm_pic.h"

void pic_init(void){  
} // pic_init

void pic_set(int kpa, int kpb, int kia, int kib, int kda, int kdb){

  uint8_t out[32];

  sprintf((char*)out, "%c%c%c%d%c\n", ':', 'a', 'g', kpa, ';');
  UARTSendNullTerminated(0, out);  // envia para UART 0 
  sprintf((char*)out, "%c%c%c%d%c\n", ':', 'b', 'g', kpb, ';');
  UARTSendNullTerminated(1, out);  // envia para UART 1
  sprintf((char*)out, "%c%c%c%d%c\n", ':', 'a', 'd', kda, ';');
  UARTSendNullTerminated(0, out);  // envia para UART 0 
  sprintf((char*)out, "%c%c%c%d%c\n", ':', 'b', 'd', kdb, ';');
  UARTSendNullTerminated(1, out);  // envia para UART 1
  sprintf((char*)out, "%c%c%c%d%c\n", ':', 'a', 'i', kia, ';');
  UARTSendNullTerminated(0, out);  // envia para UART 0 
  sprintf((char*)out, "%c%c%c%d%c\n", ':', 'b', 'i', kib, ';');
  UARTSendNullTerminated(1, out);  // envia para UART 1
}

void pic_sendToPIC(uint8_t portNum, pic_Data data) {
  uint8_t out[32];
  sprintf((char*)out, "%c%c%c%d%c\n", data.SOT, data.ADD, data.COM, data.VAL, data.EOT);
  UARTSendNullTerminated(portNum, out);  // envia também para UART 0 ou 1
  //UARTSend(portNum, out, 23); // [jo:231004] alternativa linha acima sem NULL no final
} // pic_sendToPIC

extern uint8_t pic_receiveCharFromPIC(uint8_t portNum) {
  return UARTGetChar(portNum, false);
} // pic_receiveFromPIC
