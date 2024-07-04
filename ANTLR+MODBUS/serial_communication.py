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
            self.trajectoryFile += "{:03d}".format(int(ctx.coordx().coord().getText()))
        else:
            self.trajectoryFile += "000"
        if ctx.coordy() is not None:
            self.trajectoryFile += "{:03d}".format(int(ctx.coordy().coord().getText()))
        else:
            self.trajectoryFile += "000"

        self.linha_ponto += 1



def varreGCode():
    # Processamento do arquivo GCode
    with open("ANTLR+MODBUS/GCode-example") as file:
        data = f'{file.read()}'
    lexer = GCodeLexer(InputStream(data))
    stream = CommonTokenStream(lexer)
    parser = GCodeParser(stream)
    tree = parser.gcode()
    listener = WalkListener(ser)
    walker = ParseTreeWalker()
    walker.walk(listener, tree)
    return (listener.linha_ponto, listener.traj)


global ser 


global comandoAtivo
comandoAtivo = 0

global linha
linha=0

def init_serial():
    global ser
    ser = serial.Serial(
        port='COM15',
        baudrate=115200,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=0.5,
    )
            

def send_modbus_message_pause():
    msg = b':010602010115\r\n\r'
    ser.write(msg)
    print(f"Enviado comando PAUSE: {msg}")

def send_modbus_message_start():
    msg = b':010602000116\r\n\r'
    ser.write(msg)
    print(f"Enviado comando start: {msg}")

def send_modbus_message_stop():
    msg = b':010602020114\r\n\r'
    ser.write(msg)
    print(f"Enviado comando start: {msg}")

def ativa_resposta(resposta):
    global linha
    if resposta == b'S': # Se receber 'S', envia o comando de start
        send_modbus_message_start()
    elif resposta == b's':
        send_modbus_message_stop()
    elif resposta == b'p':
        send_modbus_message_pause()

    elif resposta[0:7] == b':010301':
        linha = int(resposta[7:9].decode(), 16)
        print(f"Linha atual: {linha + 1}")
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

def comando(comando): #### CHECK ####
    global ser
    global comandoAtivo

    comandoAtivo = True
    ser.write(comando)
    print("Enviado: ", comando)
    
    resposta = ser.read(16)
    comandoAtivo = False
    ativa_resposta(resposta)
    if resposta:
        print("Resposta:", resposta)

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
    
    time.sleep(5)
    resposta = ser.read(100)
    ativa_resposta(resposta)
    print("Resposta recebida:", resposta)

def parametros(): #### CHECK #### AINDA FALTA CHAMAR A FUNÇÃO
    global ser

    #definir de acordo com o que for necessário

    kpa = 0
    kia = 0
    kda = 0
    kpb = 0
    kib = 0
    kdb = 0
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
    global comandoAtivo
    global ser

    # comando para pegar linha
    ser.write(b':0103000379' + b'\x0D\x0A' )
    
    # se não tiver um comando ativo, le a resposta
    if(not comandoAtivo): 
        resposta = ser.read(14)
        ativa_resposta(resposta)
        print("Linha:", linha)

def main():
    global ser
    init_serial()
    parametros()
    while(1):
        time.sleep(3)
        e = input()
        print(e)
        ser.write(b':010602000116\r\n\r')
                
main()