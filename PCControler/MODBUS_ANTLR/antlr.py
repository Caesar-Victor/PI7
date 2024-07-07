from .antlr_files import *
import datetime

class WalkListener(GCodeListener):    
    def __init__(self):
        self.x_point = []
        self.y_point = []

    def enterStatement(self, ctx):
        if ctx.coordx() is not None:
            text = ctx.coordx().coord().getText()
            self.x_point.append(text)
        if ctx.coordy() is not None:
            text = ctx.coordy().coord().getText()
            self.y_point.append(text)
            
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

            
"""
def varreGCode(file_name:str="G_codes/GCode1"):
    with open(file_name) as file:
        data = f'{file.read()}'
    lexer = GCodeLexer(InputStream(data))
    stream = CommonTokenStream(lexer)
    parser = GCodeParser(stream)
    tree = parser.gcode()
    listener = WalkListener()
    walker = ParseTreeWalker()
    walker.walk(listener, tree)
    
    x_pos = listener.x_point
    y_pos = listener.y_point
    
    g_list = []
    for i in range(len(x_pos)):
        g_list.append((int(x_pos[i]),int(y_pos[i])))    
    return g_list
"""