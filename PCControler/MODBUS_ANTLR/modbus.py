from .serial_communication import *
from .antlr import *
import time


global SER
SER = SerialConnection()



def send_modbus_message_pause():
    msg = b':010602010115\r\n\r'
    SER.write(msg)
    print(f"Enviado comando PAUSE: {msg}")

def send_modbus_message_start():
    global ativo
    msg = b':010602000116\r\n\r'
    SER.write(msg)
    print(f"Enviado comando start: {msg}")

def send_modbus_message_stop():
    msg = b':010602020114\r\n\r'
    SER.write(msg)
    print(f"Enviado comando stop: {msg}")

def send_modbus_init_point():
    ponto_inicial = b':011501000420'
    ponto_inicial += calculaLRC(ponto_inicial).encode()
    ponto_inicial += b'\x0D\x0A'
    SER.write(ponto_inicial)
    print(f"Mensagem de ponto inicial enviada: {ponto_inicial}" )

def protocolo_modbus(x):
    if x == "S": # Se receber 'S', envia o comando de start
        send_modbus_message_start()
    elif x == "s":
        send_modbus_message_stop()
    elif x == 'p':
        send_modbus_message_pause()
    elif x == 'i':
        print("Enviado posicao inicial")
        send_modbus_init_point()
    else:
        pass

def calculaLRC(data): #### CHECK ####
    lrc = 0
    for byte in data:
        lrc = (lrc + byte) & 0xFF
    lrc -= 0x3A
    lrc = ((lrc ^ 0xFF) + 1) & 0xFF

    lrc_string = hex(lrc)[2:]
    return lrc_string


# Função para enviar mensagem Modbus que
def traj_envio(): #### CHECK ####
    global SER
    total_pontos, traj = varreGCode()
    
    #Converte o número de pontos pointsNumber para um 
    #formato hexadecimal de dois dígitos.

    total_pontos = "{:02X}".format(total_pontos) 
    
    # mensagem para indicar que vão SER enviados total_pontos pontos
    mensagem = b':0115' + total_pontos.encode()  + traj.encode()
    mensagem += calculaLRC(mensagem).encode() + b'\x0D\x0A'
    SER.write(mensagem)
    print("Mensagem de trajetória:", mensagem)
    
    time.sleep(3)


def parametros(kpa, kia, kda, kpb, kib, kdb): #### CHECK #### AINDA FALTA CHAMAR A FUNÇÃO
    global SER
    # Send the data
    msg = b':010806'
    msg += ("{:03d}".format(kpa).encode())
    msg += ("{:03d}".format(kia).encode())
    msg += ("{:03d}".format(kda).encode())
    msg += ("{:03d}".format(kpb).encode())
    msg += ("{:03d}".format(kib).encode())
    msg += ("{:03d}".format(kdb).encode())
    msg += calculaLRC(msg).encode()
    msg += b'\x0D\x0A'
    SER.write(msg)
    print(msg)


def main():
    global SER
    kpa = int(input("Digite o valor de kpa: "))
    kia = int(input("Digite o valor de kia: "))
    kda = int(input("Digite o valor de kda: "))
    kpb = int(input("Digite o valor de kpb: "))
    kib = int(input("Digite o valor de kib: "))
    kdb = int(input("Digite o valor de kdb: "))

    parametros(kpa, kia, kda, kpb, kib, kdb)

    e = ""
    traj_envio()
    print('Ready: ')
    while(1):
        time.sleep(1)
        e = input("Modo de execucao (S, s, p, i): ")

        protocolo_modbus(e)    

        if e == 'e':
            break

        
                
#main()

