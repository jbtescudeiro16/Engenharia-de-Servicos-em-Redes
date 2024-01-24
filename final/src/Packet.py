FRAME_WIDTH = 440
FRAME_HEIGHT = 300
Packet_size = 64000 

'''
Classe que define o pacote que onde a informação sobre os frames é passada 
'''
class Packet:
    def __init__(self, info, n, framepart, Frame):
        self.info = info
        self.frameNumber = n
        self.framePart = framepart
        self.frame = Frame

    # getters
    def getInfo(self):
        return self.info
    
    def getFrameNumber(self):
        return self.frameNumber
    
    def getFramePart(self):
        return self.framePart

    def getFrame(self):
        return self.frame

    # Metodo que construi o pacote em bytes para ser enviado via socket
    def buildPacket(self):
        info_bytes = self.info.encode('utf-8')
        frame_bytes = self.frame

        padding_size = Packet_size - (4 + len(info_bytes) + 4 + len(frame_bytes))
        packet_data = (
            len(info_bytes).to_bytes(4, byteorder='big') +
            info_bytes +
            self.frameNumber.to_bytes(4, byteorder='big') +
            self.framePart.to_bytes(4, byteorder='big') +
            len(frame_bytes).to_bytes(4, byteorder='big') +
            frame_bytes +
            b'\x00' * padding_size
        )
        return packet_data

    # Metodo que estrai o conteudo do pacote para a estrutura de dados defenida
    def parsePacket(self, data):
        offset = 0
        name_size = int.from_bytes(data[offset:offset + 4], byteorder='big')
        offset += 4
        self.info = data[offset:offset + name_size].decode('utf-8')
        offset += name_size
        self.frameNumber = int.from_bytes(data[offset:offset + 4], byteorder='big')
        offset += 4
        self.framePart = int.from_bytes(data[offset:offset + 4], byteorder='big')
        offset += 4
        frame_size = int.from_bytes(data[offset:offset + 4], byteorder='big')
        offset += 4
        self.frame = data[offset:offset + frame_size]