import socket 
from auxiliarFunc import *
import threading
import queue
import time
import cv2
import tkinter as tk
from PIL import ImageTk
from connectionProtocol import *
import wave

class Stream:
    pass

class ServerGUI:

    def __init__(self, file):
        #self.IP = getIP
        self.IP = '127.0.0.2'
        self.ipDoRP = None
        self.portaDoRP = None
         # Inicializa a janela Tkinter
        self.janela = tk.Tk()
        self.janela.geometry("+100+50")
        self.janela.title("Video Stream Client")

        # Inicializa uma label para exibir os frames recebidos
        self.label = tk.Label(self.janela)
        self.label.pack()

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.videoList = []
        self.streamQueue = queue.Queue()
        self.parse(file)
        self.serverStarter()

    def parse(self, file):
        print("Parsing...")
        with open(file, 'r') as f:
            read = False
            for line in f:
                if f"ip- {self.IP}" in line:
                    read = True
                if read:
                    if "------" in line:
                        break
                    elif "ip_rp- " in line:
                        self.ipDoRP = extrair_conteudo(line)
                    elif "porta_rp- " in line:
                        self.portaDoRP = extrair_numero_porta(line)
                    elif "stream- " in line:
                        file = extrair_conteudo(line)
                        filename = getVideoName(file)
                        self.videoList.append((filename, file))

    def serverStarter(self):
        print("Starter...")
        self.conectToRP()
        self.streamStarter()
        self.server_socket.close()
    
    def conectToRP(self):
        try:
            server_address = (self.ipDoRP, self.portaDoRP)
            self.server_socket.connect(server_address)
            print("Servidor conectado ao RP")
    
            # enviar os videos que você tem para exibir
            for video in self.videoList:
                msg = f"{video[0]}-ADD-".encode('utf-8')
                self.server_socket.sendall(msg)

            print("RP informado dos vídeos que o servidor tem disponíveis...")
        except Exception as e:
            print(f"Erro ao conectar ou enviar mensagens: {e}")

    def streamStarter(self):
        print("Server à espera de pedidos de Stream do RP")
        while True:
            data = self.server_socket.recv(1024)
            if not data:
                break
            mensagem = data.decode('utf-8')
            if "Stream- " in mensagem:
                self.streamQueue.put(extrair_conteudo(mensagem))
                thread = threading.Thread(target=self.sendStream)
                thread.start()
                self.janela.mainloop()


    def sendStream(self):
        streamName = self.streamQueue.get()
        print(f"Vou streamar o video: {streamName}")
        streampath = None
        for video in self.videoList:
            if video[0]== streamName:
                streampath = video[1]
        if streampath:
            sstream = cv2.VideoCapture(streampath)
            fps =  sstream.get(cv2.CAP_PROP_FPS)
            frame_interval = 1.0 / fps
            st = time.time()
            i = 0
            try:
                while sstream.isOpened():
                    print("Frame: ",i)
                    ret, frame = sstream.read()
                    if not ret:
                        break
                    
                    pacote = Packet()
                    pacote.initial1(streamName, frame)
                    self.server_socket.send(pacote.buildPacket())
                    
                    # Calcule o tempo decorrido desde o último envio
                    elapsed_time = time.time() - st

                    # Aguarde o tempo restante para manter a taxa de quadros
                    time.sleep(max(0, frame_interval - elapsed_time))

                    st = time.time()

                    # Converte os dados do frame em uma imagem
                    img = ImageTk.PhotoImage(data=pacote.frame_data)

                    # Atualiza a label na janela Tkinter com a nova imagem
                    self.label.configure(image=img)
                    self.label.image = img
                    self.janela.update()
                    i+=1
            finally:
                print('Player closed')


if __name__ == "__main__":
    try:
        filename = "config_file.txt"

        # Criar um Servidor
        rp = ServerGUI(filename)
    except:
        print("[Usage: Server.py]\n")	