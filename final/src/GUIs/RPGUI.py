import socket
import threading
import tkinter as tk
import time
from src.auxiliarFunc import *
from src.Stream import *
from src.NodeData import *
from src.Packet import *

'''
Esta é a classe principal para o RendezvousPoint
'''
MaintenanceTime = 5
class RPGUI:
    def __init__(self, node):
        self.node = node
        self.clients_logged = {}
        self.streamList = {}
        self.networkUpdateNumber = 0
        self.caminhos = []
        self.clientBestTrack = {}
        self.janela = None
        self.condition = threading.Condition()
        self.conditionBool = False
        self.startRP()

    def startRP(self):
        print("Starting...")
        thread0 = threading.Thread(target=self.NodeConnection)
        thread1 = threading.Thread(target=self.clientConnection)
        thread2 = threading.Thread(target=self.serverConnection)
        thread3 = threading.Thread(target=self.streamConnection)
        thread0.start()
        thread1.start()
        thread2.start()
        thread3.start()

    #-----------------------------------------------------------------------------------------
    # Tratamento de Nós
    def NodeConnection(self):
        thread = threading.Thread(target=self.recieveNodeConnection)
        thread.start()
        self.startNetwork()
        self.sendNodeConnection()
        self.NetworkMaintenance()

    '''Metodo que cria uma interface grafica que permite ao RP construir a rede apos selecionar essa 
    opção indicada. Esta funcionalidade permite garantir que a rede so é estabelecida depois de todos
    os nodos estiverem ligados'''
    def startNetwork(self):
        self.janela = tk.Tk()
        self.janela.title(f'RendezvousPoint: {NodeData.getIp(self.node)}')
        self.label = tk.Label(self.janela, width=60, padx=10, pady=10)
        self.label["text"] = "Deseja construir a rede overlay?"
        self.label.grid(row=0, column=0, padx=10, pady=10)	
        self.botaoStart = tk.Button(self.janela, width=30, padx=10, pady=10)
        self.botaoStart["text"] = "Start"
        self.botaoStart["command"] = self.startTest
        self.botaoStart.grid(row=1, column=0, padx=10, pady=10)
        self.janela.mainloop()
        with self.condition:
            while not self.conditionBool:
                self.condition.wait()
        self.conditionBool = False
    def startTest(self):
        with self.condition:
            self.conditionBool = True
            self.condition.notify()
        self.janela.destroy()
    
    '''Metodo responsavel por enviar a mensagem de "Update Network" aos nodos vizinhos que iram fazer o 
    mesmo para que seja possivel iniciaram a construção da rede no sentido inverso'''
    def sendNodeConnection(self):
        print("RP asked for an update on the Network | current nª:",self.networkUpdateNumber)
        try:
            msg = f"Update Network-{self.networkUpdateNumber}"
            self.networkUpdateNumber += 1
            msg_data = (
                len(msg).to_bytes(4, 'big') +
                msg.encode('utf-8')
            )
            for node in NodeData.getNeighboursAddress(self.node):
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as node_starter_socket:      
                        node_adress = (node, NodeData.getNodePort(self.node))
                        node_starter_socket.connect(node_adress)
                        node_starter_socket.sendall(msg_data)
                except Exception:
                    print("Erro ao enviar mensagem de iniciar a rede para o no: ", node)
                finally:
                    node_starter_socket.close()
        except Exception as e:
            print("Erro ao testar a rede overlay: ", e)
        finally:
            node_starter_socket.close()
        
    '''Metodo responsavel por receber os caminhos provenientes de todos os nodos e inverte-os por virem 
    no sentido contrario e guarda essa informação construindo assim a rede overlay 
    é ainda atualizado o caminho mais curto para cada cliente segunda a metrica do metodo updateBestTrack'''
    def recieveNodeConnection(self):
        socket_address = (NodeData.getIp(self.node), NodeData.getNodePort(self.node))
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as node_socket:
                node_socket.bind(socket_address)
                node_socket.listen()
                print("RP waiting for Node connections: ", socket_address)
                while True:
                    client_connection,_ = node_socket.accept()

                    size = client_connection.recv(4)
                    msg_size = int.from_bytes(size, byteorder='big')

                    msg_data = client_connection.recv(msg_size)
                    mensagem = msg_data.decode('utf-8')
                    
                    if "Update Network" not in mensagem:
                        mensagem = mensagem + " <- " + NodeData.getIp(self.node)
                        cam = inverter_relacoes(mensagem)
                        #print("New connection: ", cam)
                
                        if ":clst-" in mensagem:
                            caminho, cliente_st, updateNumber = getTrackAndTimeAndUpdateNumber(cam)
                            self.caminhos.append(caminho)
                            self.updateBestTrack(caminho, cliente_st, updateNumber)
                        else:
                            self.caminhos.append(cam)
                    
                    client_connection.close()
        except Exception as e:
            print(f"Erro na receção dos caminhos para os Nós no RP: ",e)
        finally:
            node_socket.close()

    ''' Metodo onde a cada período fixo de segundos é efetuado um novo teste de conexão e após 
    essa receção são avaliados os caminhos otimos para enviar um pacote para cada cliente'''
    def NetworkMaintenance(self):
        try:
            while True:
                time.sleep(MaintenanceTime)
                self.sendNodeConnection()

        except Exception as e:
            print("Erro na manutenção da rede Overlay: ", e)

    ''' Metodo que avalia se o novo caminho é o mais rapido para chegar ao cliente se sim atualiza-o
    Se o cliente estiver a ver uma Transmissão essa alteração do melhor caminho é indicada e utilizada'''
    def updateBestTrack(self, new_track, client_st, updateNumber):
        try:
            Updated = False
            client_IP = getClientIP(new_track)
            end_time = time.time()
            elapsed_time = end_time - client_st
            
            if not self.clientBestTrack.get(client_IP):
                self.clientBestTrack[client_IP] = (new_track, elapsed_time, updateNumber)
            else:
                current_track, current_time, current_updateNumber = self.clientBestTrack[client_IP]
                # Atualizar a cada Network Update
                if current_updateNumber < self.networkUpdateNumber - 1:
                    self.clientBestTrack[client_IP] = (new_track, elapsed_time, updateNumber)
                    Updated = True
                # Caso seja outro caminho possivel se o tempo for menor optar pelo caminho
                elif current_updateNumber == self.networkUpdateNumber - 1 and elapsed_time < current_time:
                    self.clientBestTrack[client_IP] = (new_track, elapsed_time, updateNumber)
                    Updated = True
                # Se o caminho for diferente e o cliente estiver a ver uma transmissao mudar  
                if current_track != new_track and Updated and self.clients_logged.get(client_IP):
                    streamNameClientIsWatching = self.clients_logged[client_IP]
                    stream = self.streamList[streamNameClientIsWatching]
                    StreamController.updateTrackToClientList(stream, client_IP, new_track) 
        except Exception as e:
            print("Erro na atualização do melhor caminho para o cliente: ",e)
        finally:
            if Updated:
                print("Lista de caminhos para os clientes:")
                for i in self.clientBestTrack.keys():
                    print(f"\tIP[{i}] TRACK[{self.clientBestTrack[i][0]}] TIMESTAMP[{self.clientBestTrack[i][1]}] Update nª[{self.clientBestTrack[i][2]}]")

    #-----------------------------------------------------------------------------------------
    # Tratamento de Clientes
    def clientConnection(self):
        socket_address = (NodeData.getIp(self.node), NodeData.getPortaClient(self.node))
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socketForClient:
            socketForClient.bind(socket_address)
            socketForClient.listen(1)
            print("RP waiting for Client connections: ", socket_address)
            try:
                while True:
                    conn, addr = socketForClient.accept()
                    thread = threading.Thread(target=self.initialClientConn, args=(conn, addr))
                    thread.start()
            finally:
                socketForClient.close()
    
    # Metodo que trata de receber as conexões de clientes e consuante a sua escolhade stream
    # trata de os adicionar à Stream indicada 
    # tambem quando um cliente decide deixar de assitir uma stream trata de o remover dessa stream
    # e avisa ainda o servidor no caso de não exitir nenhum cliente a assistir 
    def initialClientConn(self, conn, addr):
        try:
            size = conn.recv(4)
            msg_size = int.from_bytes(size, byteorder='big')

            msg_data = conn.recv(msg_size)
            mensagem = msg_data.decode('utf-8')
                    

            if mensagem == "VideoList":
                if not self.streamList:
                    noVidmsg = "I DONT HAVE STREAMS"
                    data = (
                        len(noVidmsg.encode('utf-8')).to_bytes(4, 'big') +
                        noVidmsg.encode('utf-8')
                    )
                    conn.sendall(data)
                else:
                    msg = ""
                    for stream in self.streamList.keys():
                        msg += stream+"/"    
                    data = msg.encode('utf-8')
                    dataToSend = (
                        len(data).to_bytes(4,'big') +
                        data
                    )
                    conn.sendall(dataToSend)
            
                    size = conn.recv(4)
                    msg_size = int.from_bytes(size, byteorder='big')

                    msg_data = conn.recv(msg_size)
                    recv_msg = msg_data.decode('utf-8')
                    
                    selectedStream = extrair_texto(recv_msg)
                    stream = self.streamList[selectedStream]
                    self.clients_logged[addr[0]] = selectedStream
                    
                    StreamController.addClient(stream, addr[0], self.clientBestTrack[addr[0]][0])
                    print(f"Client {addr} connected and watching Stream {selectedStream}")

            elif mensagem == "Connection closed":
                stream_do_cliente = self.clients_logged[addr[0]]
                stream = self.streamList[stream_do_cliente]
                StreamController.rmvClient(stream, addr[0])
            
                del self.clients_logged[addr[0]]
                print(f"Client {addr[0]} disconnected from {stream.name}.")

        except Exception as e:
            print(f"Erro no processamento do cliente {addr[0]}: {e}")
        finally:
            conn.close()

    #-----------------------------------------------------------------------------------------
    # Tratamento de Servidores
    def serverConnection(self):
        socket_address = (NodeData.getIp(self.node), NodeData.getPortaServer(self.node))
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socketForServer:
            socketForServer.bind(socket_address)
            socketForServer.listen(1)
            print("RP waiting for Server connections: ", socket_address)
            try:
                while True:
                    conn, addr = socketForServer.accept()
                    print(f"Server {addr} connected!")
                    thread = threading.Thread(target=self.initialServerConnection, args=(conn, addr))
                    thread.start()
            finally:
                socketForServer.close()
    
    # Metodo que trata de receber conexões de servidores e as suas listas de streams
    # para cada stream que o servidor é capaz de transmitir é criada uma estrutura stream
    # com a informação do servidor que tem essa stream assim como o seu nome 
    def initialServerConnection(self, conn, addr):
        try:
            # receber mensagens com a lista das streams
            size = conn.recv(4)
            msg_size = int.from_bytes(size, byteorder='big')

            msg_data = conn.recv(msg_size)
            mensagem = msg_data.decode('utf-8')
                    
            if "-AND-" in mensagem:
                lista_de_videos = mensagem.split('-AND-')
            else:
                lista_de_videos = [mensagem]
            
            # Cria uma Stream por transmissao de cada servidor
            for videoname in lista_de_videos:
                stream = StreamController(videoname, NodeData.getStreamPort(self.node), (addr[0],NodeData.getPortaServer(self.node)))
                self.streamList[stream.name] = stream
            
            print(f'Stream list updated with: {lista_de_videos}')
        except Exception as e:
            print(f"Erro no processamento do servidor {addr[0]}: {e}")
        
    #-----------------------------------------------------------------------------------------
    # Receber de Streams e enviar

    # Metodo responsavel por lidar com as mensagens de transmissão de frame do servidor para os respetivos
    # clientes seguindo o caminho previamente definido 
    # recebe o pacote com o nome da stream e consuante esse nome refaz o pacote com o caminho a percorrer
    # e envia para o respectivo nodo vizinho nesse caminho
    def streamConnection(self):
        my_address = (NodeData.getIp(self.node), NodeData.getStreamPort(self.node))
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as socketForStream:
            try:
                socketForStream.bind(my_address)
                print("RP waiting for Stream connections: ", my_address)
                while True:
                    data, _ = socketForStream.recvfrom(Packet_size)
                    
                    # Parse the packet using your Packet class
                    received_packet = Packet("", "", "", "")
                    received_packet.parsePacket(data)
                    stream = self.streamList[received_packet.info]
                    
                    StreamController.sendStream(stream, received_packet.frameNumber, received_packet.framePart, received_packet.frame)
            except Exception as e:
                print(f"Error in streamConnection: {e}")
            finally:
                socketForStream.close()                