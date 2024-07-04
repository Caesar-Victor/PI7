from antlr4 import *
from GCodeLexer import GCodeLexer
from GCodeParser import GCodeParser
from GCodeListener import GCodeListener
import serial as sc
import serial.tools.list_ports
import time

class WalkListener(GCodeListener):
    def __init__(self, serial):
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
    return (data, listener.linha_ponto, listener.traj)



# Constantes para os estados
ESPERANDO_TRAJ = 0
INATIVO = 1
ATIVO = 2
PAUSADO = 3

# Constantes para os eventos
SEM_EVENTO = 0
TRAJ_CARREGADA = 1
START = 2
PAUSE = 3
RESUME = 4
STOP = 5

global estado
global ser 

estado = ESPERANDO_TRAJ

global comandoAtivo
comandoAtivo = 0
global linha
linha=0

def init_serial():
    global ser
    ports = list(serial.tools.list_ports.comports())
    com5_available = any(port.device == 'COM5' for port in ports)
    
    if com5_available:
        try:
            ser = serial.Serial(
                port='COM5',
                baudrate=115200,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS,
                timeout=0.5,
            )
            print("COMx aberto com sucesso!")
        except serial.SerialException as e:
            print(f"Erro: {e}")
    else:
        print("COMx não disponível!")

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
    global estado
    if resposta == b'S': # Se receber 'S', envia o comando de start
        send_modbus_message_start()
    elif resposta == b's':
        send_modbus_message_stop()
    elif resposta == b'p':
        send_modbus_message_pause()
    elif resposta == b't':



    if resposta== b':010602000116\r\n\r':
        if state == INATIVO:
            state = ATIVO
            print("Start.")
    elif resposta== b':0115010177\r\n\r':
        state == INATIVO
        state = INATIVO
        print("Traj. in.")
    elif resposta == b':010602010115\r\n\r':
        if state == ATIVO:
            state = PAUSADO
            print("Pause.")
    elif resposta == b':010602030113\r\n\r':
        if state == PAUSADO:
            state = ATIVO
            print("Resume.")
    elif resposta == b':010602020114\r\n\r':
        if state == ATIVO or state == PAUSADO:
            state = INATIVO
            linha = 0
            print("Stop.")
    elif resposta[0:7] == b':010301':
        linhaAtual = int(resposta[7:9].decode(), 16)
        print(f"Linha atual: {linhaAtual + 1}")
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
    data, total_pontos, traj = varreGCode()
    
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
    kpA = 0
    kiA = 0
    kdA = 0
    kpB = 0
    kiB = 0
    kdB = 0
    # Send the data
    msg = b':010806'
    msg += ("{:03d}".format(kpA).encode())
    msg += ("{:03d}".format(kiA).encode())
    msg += ("{:03d}".format(kdA).encode())
    msg += ("{:03d}".format(kpB).encode())
    msg += ("{:03d}".format(kiB).encode())
    msg += ("{:03d}".format(kdB).encode())
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



