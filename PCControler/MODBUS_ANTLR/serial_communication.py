import serial as sc

class SerialConnection:
    def __init__(self):
        self.serial_connection = None
        self.init_serial()
    
    def init_serial(self):
        for i in range(10):
            try:
                self.serial_connection = sc.Serial(
                    port=f'/dev/ttyACM{i}',
                    baudrate=115200,
                    parity=sc.PARITY_NONE,
                    stopbits=sc.STOPBITS_ONE,
                    bytesize=sc.EIGHTBITS,
                    timeout=0.5,
                )
            except sc.SerialException as e:
                pass
        
    def write(self, data):
        self.serial_connection.write(data)
        
    def read(self):
        return self.serial_connection.read()
    
    def close(self):
        self.serial_connection.close()
        
