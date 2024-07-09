from antlr4 import *
from GCodeLexer import GCodeLexer
from GCodeParser import GCodeParser
from GCodeListener import GCodeListener
import serial as sc
import serial.tools.list_ports
import time

class WalkListener(GCodeListener):
    def __init__(self):
        self.traj=""
        self.linha_ponto=0

    def enterStatement(self, ctx):
        if ctx.codfunc() is not None:
            pass
        if ctx.coordx() is not None:
            self.traj += "{:03d}".format(int(ctx.coordx().coord().getText()))
        else:
            self.traj += "000"
        if ctx.coordy() is not None:
            self.traj += "{:03d}".format(int(ctx.coordy().coord().getText()))
        else:
            self.traj += "000"

        self.linha_ponto += 1



def varreGCode():
    # Processamento do arquivo GCode
    with open("ANTLR+MODBUS/GCode-example") as file:
        data = f'{file.read()}'
    lexer = GCodeLexer(InputStream(data))
    stream = CommonTokenStream(lexer)
    parser = GCodeParser(stream)
    tree = parser.gcode()
    listener = WalkListener()
    walker = ParseTreeWalker()
    walker.walk(listener, tree)
    return (listener.linha_ponto, listener.traj)


global ser 
global linha
linha=0

def init_serial():
    global ser
    for i in range(2):
        try:
            ser = serial.Serial(
                port=f'/dev/ttyACM{i}',
                baudrate=115200,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS,
                timeout=0.5,
            )
        except serial.SerialException as e:
            print(f"Erro: {e}")
            

def send_modbus_message_pause():
    msg = b':0106010177\r\n\r'
    ser.write(msg)
    print(f"Enviado comando PAUSE: {msg}")

def send_modbus_message_start():
    global ativo
    msg = b':0106000178\r\n\r'
    ser.write(msg)
    print(f"Enviado comando start: {msg}")

def send_modbus_message_continue():
    msg = b':0106030175\r\n\r'
    ser.write(msg)
    print(f"Enviado comando Continue: {msg}")

def send_modbus_message_stop():
    msg = b':0106020176\r\n\r'
    ser.write(msg)
    print(f"Enviado comando stop: {msg}")

def send_modbus_init_point():
    ponto_inicial = b':011501000420'
    ponto_inicial += calculaLRC(ponto_inicial).encode()
    ponto_inicial += b'\x0D\x0A'
    ser.write(ponto_inicial)
    print(f"Mensagem de ponto inicial enviada: {ponto_inicial}" )

def protocolo_modbus(x):
    global linha
    if x == "S": # Se receber 'S', envia o comando de start
        send_modbus_message_start()
    elif x == "c":
        send_modbus_message_stop()
    elif x == 'p':
        send_modbus_message_pause()
    elif x == 's':
        send_modbus_message_continue()
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
    global ser
    total_pontos, traj = varreGCode()
    
    #Converte o número de pontos pointsNumber para um 
    #formato hexadecimal de dois dígitos.

    total_pontos = "{:02X}".format(total_pontos) 
    
    # mensagem para indicar que vão ser enviados total_pontos pontos
    mensagem = b':0115' + total_pontos.encode()  + traj.encode()
    mensagem += calculaLRC(mensagem).encode() + b'\x0D\x0A'
    ser.write(mensagem)
    print("Mensagem de trajetória:", mensagem)
    
    time.sleep(3)


def parametros(kpa=1, kia=0, kda=0, kpb=1, kib=0, kdb=0): #### CHECK #### AINDA FALTA CHAMAR A FUNÇÃO
    global ser

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
    ser.write(msg)
    print(msg)

# Basicamente, a função obtem_linha() pode ser chamada para obter a linha atual

def obtem_linha(): #### CHECK ####
    global linha
    global ser

    # comando para pegar linha
    ser.write(b':0103000379' + b'\x0D\x0A' )
    

def main():
    global ser
    init_serial()
    kpa = 5# int(input("Digite o valor de kpa: "))
    kia = 0#int(input("Digite o valor de kia: "))
    kda = 0#int(input("Digite o valor de kda: "))
    kpb = 5#int(input("Digite o valor de kpb: "))
    kib = 0#int(input("Digite o valor de kib: "))
    kdb = 0#int(input("Digite o valor de kdb: "))

    parametros(kpa, kia, kda, kpb, kib, kdb)
    #parametros()

    e = ""
    traj_envio()
    print('Ready: ')
    while(1):
        time.sleep(1)
        e = input("Modo de execucao (S, s, p, c, i)(e)xit: ")

        protocolo_modbus(e)    

        if e == 'e':
            break

        
                
main()