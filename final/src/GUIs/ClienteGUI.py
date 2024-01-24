import tkinter as tk
import socket
import threading
from PIL import ImageTk
from src.Packet import *
from src.NodeData import *
import time

'''
Esta é a classe principal para o Cliente
'''
class ClienteGUI:
    def __init__(self, janela, node):
        self.node = node
        self.janela = janela
        self.janela.title(f"Cliente {NodeData.getIp(node)}")
        self.selection_widgets = []
        self.my_address = (NodeData.getIp(self.node), 0)
        self.selected = None
        self.condition = threading.Condition()
        self.conditionBool = False
        self.status = "Playing"
        self.packetQueue = []
        threading.Thread(target=self.clientStart).start()
        
    def clientStart(self):
        try:
            while True:
                self.status = "Playing"
                self.inicialConnection()
                self.recievestreamTransmission()
        except Exception as e:
            print(e)
    '''
    Este metodo é usadado para conectar o cliente ao RendezvousPoint onde nessa conexão o cliente
    é informado de quais streams os servidores podem streamar, e atraves de uma interface gráfica 
    é possivel selecionar um deles, após selecionado é enviada essa informação ao RP
    '''
    def inicialConnection(self):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as rp_socket:
                rp_socket.bind(self.my_address)
                rp_socket.connect(NodeData.getRPAddress(self.node))
        
                # Perguntar ao RP quais as Streams que ele tem acesso
                data = ("VideoList").encode('utf-8')
                dataToSend = (
                    len(data).to_bytes(4, 'big') +
                    data
                )
                rp_socket.sendall(dataToSend)
                
                # Receber a lista de streams do RP
                size = rp_socket.recv(4)
                msg_size = int.from_bytes(size, byteorder='big')

                msg_data = rp_socket.recv(msg_size)
                mensagem = msg_data.decode('utf-8')

                vids = mensagem.split("/")
                vids.pop()
                # Selecionar a transmissão
                self.askStreamTransmission(vids)

                # Enviar a escolha para o RP
                msg = f"Stream- {self.selected}".encode('utf-8')
                dataToSend = (len(msg).to_bytes(4,'big')+msg)
                rp_socket.sendall(dataToSend)
                
        except Exception as e:
            print(f"Erro ao conectar ou enviar mensagens: {e}")
        finally:
            rp_socket.close()
    '''
    Metodos usados para definir a interface gráfica que permite ao cliente selecionar uma opção de stream
    '''
    def askStreamTransmission(self, streamList):
        # Chamar a interface gráfica
        self.clienteInterface(streamList)

        # Esperar a escolha por parte do cliente
        with self.condition:
            while not self.conditionBool:
                self.condition.wait()
        self.conditionBool = False

    # Interface gráfica
    def clienteInterface(self, streamList):
        i = 0
        spacing = 10
        for stream in streamList:
            # mostrar nome da stream
            label = tk.Label(self.janela, width=60, padx=spacing, pady=spacing)
            label["text"] = f"{stream}"
            label.grid(row=i, column=0, padx=spacing, pady=spacing)

            # Botao para selecionar a stream 		
            botaoStart = tk.Button(self.janela, width=30, padx=spacing, pady=spacing)
            botaoStart["text"] = "Select"
            botaoStart["command"] = lambda s=stream: self.selectStream(s)
            botaoStart.grid(row=i, column=1, padx=spacing, pady=spacing)

            self.selection_widgets.extend([label, botaoStart])
            i+=1
        
    # metodo que garante a seleção de uma stream
    def selectStream(self, video):
        self.selected = video
        self.conditionBool = True
        
        # Oculta ou destrói os widgets da seleção
        for widget in self.selection_widgets:
            widget.destroy()

        with self.condition:
            # Notificar que o cliente ja selecionou uma stream
            self.condition.notify()
        print(f"{video} has been selected...")
    
    '''
    Metodos que proporcionam a receção de uma stream e consequentemente mostrar essa reção ao cliente 
    atraves de uma interface gráfica
    De notar: cada frame é dividido em 2 pacotes no seu envio devido à dimensão dos mesmos e por isso 
    utilizamos metricas de controlo de perda de pacotes na receção dos mesmos
    '''
    def recievestreamTransmission(self):
        self.clienteInterface2()

        my_address_udp = (NodeData.getIp(self.node), NodeData.getStreamPort(self.node))
        try:
            # Receber os pacotes udp que transportam a informação dos frames em bytes
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as socketForStream:
                socketForStream.bind(my_address_udp)
                while self.status != "Closed":
                    # A cada iteração recebemos três pacotes que sao serializados e caso o cliente estiver a
                    # visualizar em tempo reasão, não em estado pausa, adicionados a uma lista de pacotes
                    for i in range(2):
                        data, _ = socketForStream.recvfrom(Packet_size)
                        pacote = Packet("", "", "", "")
                        Packet.parsePacket(pacote, data)
                        if self.status == "Playing": 
                            self.packetQueue.append(pacote)
                        #print("Frame: ", pacote.frameNumber)
                        i+=1

                    # Se o cliente estiver a ver a stream em tempo real, verificamos se os trẽs pacotes que formam 
                    # um frame foram recebidos e se sim criamos um frame e atualizamos a imagem na interface gráfica
                    if self.status == "Playing":
                        # verificar se é possivel criar um frame com os pacotes que temos
                        frame = self.verifyFrame()

                        # Se for possivel o frame é criado e a imagem atualizada
                        if frame:
                            # Converte os dados do frame em uma imagem
                            img = ImageTk.PhotoImage(data=frame)

                            # Atualiza a label na janela Tkinter com a nova imagem
                            self.label.configure(image=img)
                            self.label.image = img
                self.notifyCloseStream()
        except Exception as e:
            print(f"Erro ao receber vídeo: {e}")
        finally:
            # fechar a conexão udp
            socketForStream.close()

    ''' Interface Grafica'''
    def clienteInterface2(self):
        # tela de display de video
        self.label = tk.Label(self.janela, bg='white')
        self.label.grid(row=0, column=0, padx=10, pady=10, columnspan=2)

        # Butao pausa de visualização da stream pelo cliente				
        self.botaoPause = tk.Button(self.janela, width=20, padx=3, pady=3)
        self.botaoPause["text"] = "Pause"
        self.botaoPause["command"] = self.pauseStream
        self.botaoPause.grid(row=1, column=0, padx=10, pady=10)

        # Para fechar a transmissao de video para o cliente
        botaoClose = tk.Button(self.janela, width=20, padx=3, pady=3)
        botaoClose["text"] = "Close"
        botaoClose["command"] =  self.closeStream
        botaoClose.grid(row=1, column=1, padx=10, pady=10)

        self.selection_widgets.extend([self.label, self.botaoPause, botaoClose])

    '''
    Metodo de verficação e correção na perda de pacotes pela rede
    '''        
    def verifyFrame(self):
        # verificar se os 2 elementos da lista sao do mesmo pacote
        if len(self.packetQueue) >= 2:
            pack1 = self.packetQueue[0]
            pack2 = self.packetQueue[1]
            # se sim juntar e devolver o frame
            if Packet.getFrameNumber(pack1) == Packet.getFrameNumber(pack2) and Packet.getFramePart(pack1) != Packet.getFramePart(pack2):
                self.packetQueue.pop(0)
                self.packetQueue.pop(0)
                return Packet.getFrame(pack1) + Packet.getFrame(pack2)
            else:
                # caso contrario eliminar o primeiro pacote da lista de recebidos
                self.packetQueue.pop(0)
                self.verifyFrame()
        else:
            return None
       
    '''
    Metodos usados para garantir a funcionalidade dos butões na interface gráfica
    '''
    def pauseStream(self):
        # Parar de mostrar os pacotes que estamos a receber
        if self.status == "Playing":
            print("Stream paused...")
            self.status = "Pause"
            self.botaoPause["text"] = "Resume"
        # Voltar a mostrar os pacotes que esta a receber
        elif self.status == "Pause":
            print("Stream resumed...")
            self.status = "Playing"
            self.botaoPause["text"] = "Pause"

    def closeStream(self):
        # Fechar a recessão de stream
        try:
            self.status = "Closed"
        finally:
            # Oculta ou destrói os widgets da seleção
            for widget in self.selection_widgets:
                widget.destroy()
            

    def notifyCloseStream(self):
        try:
            # Avisar o RP que não pretende receber mais pacotes
            self.rp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.rp_socket.bind(self.my_address)
            self.rp_socket.connect(NodeData.getRPAddress(self.node))
            
            message = "Connection closed"
            data = message.encode('utf-8')
            dataToSend = (
                len(data).to_bytes(4, 'big') +
                data
            )
            self.rp_socket.sendall(dataToSend)
            
            print('The Client informed the RP that he no longer intends to receive the stream.')
        except Exception as e:
            print(f"Erro ao enviar mensagem de fechar a Stream para o servidor: {e}")
        finally:
            self.rp_socket.close()