import cv2
import pickle

FRAME_WIDTH = 640
FRAME_HEIGHT = 480

class Packet:
    def __init__(self):
        self.total_size = None
        self.name_size = None
        self.name_data = None 
        self.frame_data = None
        self.frame_size = None

    def initial1(self, name, Frame):
        self.name_data = name.encode('utf-8') 
        self.name_size = len(self.name_data)
        Frame = cv2.resize(Frame, (FRAME_WIDTH, FRAME_HEIGHT))
        self.frame_data = cv2.imencode('.jpg', Frame)[1].tobytes()
        self.frame_size = len(self.frame_data)

    def initial2(self, total_bytes, pacote):
        self.total_size = total_bytes
        self.parsePacket(pacote)

    def buildPacket(self):
        # Calcula o tamanho total do pacote
        self.total_size = (
            4 +  # tamanho do name_data
            self.name_size +
            4 +  # tamanho do frame_size
            self.frame_size
        )

        # Constrói o pacote com o tamanho total
        packet_data = (
            self.total_size.to_bytes(4, byteorder='big') +
            self.name_size.to_bytes(4, byteorder='big') +
            self.name_data +
            self.frame_size.to_bytes(4, byteorder='big') +
            self.frame_data 
        )
        return packet_data

    def parsePacket(self, data):
        self.name_size = int.from_bytes(data[0:4], byteorder='big')

        offset = 4
        self.name_data = data[offset:offset + self.name_size].decode('utf-8')

        offset += self.name_size
        self.frame_size = int.from_bytes(data[offset:offset + 4], byteorder='big')

        offset += 4
        self.frame_data = data[offset:offset + self.frame_size]