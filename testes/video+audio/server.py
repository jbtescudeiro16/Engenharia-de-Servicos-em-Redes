import cv2, imutils, socket
import numpy as np
import time
import base64
import threading, wave, pyaudio,pickle,struct
import sys
import queue
import os
from PIL import Image, ImageTk    
import tkinter as tk     
        
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
FPS_TARGET = 24

class Server():
    def __init__(self):
        self.IP = "127.0.0.1"
        self.porta = 12345
        self.BUFF_SIZE = 65536
        self.filename = '../VIDEO/video.mp4'
        self.audiofile = None
        self.getaudiofile()
        # Inicializa a janela Tkinter
        self.janela = tk.Tk()
        self.janela.title("Video Stream Client")

        # Inicializa uma label para exibir os frames recebidos
        self.label = tk.Label(self.janela)
        self.label.pack()

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, self.BUFF_SIZE)
        self.socket_address = (self.IP, self.porta)
        self.client_socket = None
        self.client_address = None
        self.vid = cv2.VideoCapture(self.filename)
        self.q = queue.Queue(maxsize=10)
        self.FPS = self.vid.get(cv2.CAP_PROP_FPS)
        self.TS = (0.5/self.FPS)
        self.BREAK = False
        self.start()

    def getaudiofile(self):
        partes = self.filename.split('.')
        partes.pop()
        nome_sem_extensao = '.'.join(partes)
        self.audiofile = nome_sem_extensao + "temp.wav"
        if not os.path.exists(self.audiofile):
            command = f"ffmpeg -i {self.filename} -ab 160k -ac 2 -ar 44100 -vn -f wav {self.audiofile}"
            os.system(command)

    def start(self):
        self.server_socket.bind(self.socket_address)
        self.server_socket.listen()
        print("Servidor à espera: ",self.socket_address)

        self.client_socket, self.client_address = self.server_socket.accept()
        print("Conexão aceite da", self.client_address)
        '''
        start = input("S to start: ")
        while not start == "s":
            start = input("S to start: ")
        self.send_stream()
        self.janela.mainloop()
        
        '''
        t1 = threading.Thread(target=self.video_stream2)
        t2 = threading.Thread(target=self.audio_stream)
        t1.start()
        t2.start()
        self.janela.mainloop()
        
    def send_stream(self):
        frame_rate = 25
        frame_interval = 1.0 / frame_rate
        st = time.time()

        while self.vid.isOpened():
            ret, frame = self.vid.read()
            if not ret:
                break

    def video_stream2(self):
        #fps, st, frames_to_count, cnt = (0, 0, 1, 0)
        img = None  # Inicialize a variável de imagem fora do loop
        frame_rate = 24  # Taxa de quadros desejada (25 FPS)
        frame_interval = 1.0 / frame_rate
        st = time.time()
        i = 0
        try:
            while self.vid.isOpened():
                ret, frame = self.vid.read()
                if not ret:
                    break

                frame = cv2.resize(frame, (FRAME_WIDTH, FRAME_HEIGHT))
                frame_data = cv2.imencode('.jpg', frame)[1].tobytes()

                frame_size = len(frame_data)
                self.client_socket.send(frame_size.to_bytes(4, byteorder='big'))
                self.client_socket.send(frame_data)

                
                # Calcule o tempo decorrido desde o último envio
                elapsed_time = time.time() - st

                # Aguarde o tempo restante para manter a taxa de quadros
                time.sleep(max(0, frame_interval - elapsed_time - 0.01))

                st = time.time()

                # Converte os dados do frame em uma imagem
                img = ImageTk.PhotoImage(data=frame_data)

                # Atualiza a label na janela Tkinter com a nova imagem
                self.label.configure(image=img)
                self.label.image = img
                self.janela.update()
                i+=1
        finally:
            print("frames- ",i)
            print('Player closed')
            self.BREAK = True
            self.vid.release()



    def audio_stream(self):
        s = socket.socket()
        new_address = (self.IP, (self.porta-1))
        s.bind(new_address)

        s.listen(5)
        CHUNK = 1024*2
        wf = wave.open(self.audiofile, 'rb')
        print('server listening at',new_address)
       
        client_socket,addr = s.accept()
        i=0
        data = wf.readframes(CHUNK)
        while data:
            a = pickle.dumps(data)
            message = struct.pack("Q",len(a))+a
            client_socket.sendall(message)
            data = wf.readframes(CHUNK)
            i += 1
        print("audio- ",i)
        print('Server closed')
        s.close()


if __name__ == "__main__":
    server = Server()