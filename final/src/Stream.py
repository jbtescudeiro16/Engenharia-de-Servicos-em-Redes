import socket
from src.auxiliarFunc import *
from src.Packet import *
from src.NodeData import *

'''
Esta é a classe Stream implementada para auxiliar o RP a gerenciar as Streams no que toca 
a receber e enviar dados, e gerenciar para quem continuar a mandar assim como o caminho 
por onde a informação tem de passar
'''
class StreamController():
    def __init__(self, name, nodePort, server):
        self.name = name
        self.nodePort = nodePort
        self.server_address = server
        self.status = "Closed" # "Pending" "Streaming"
        self.trackToClientesList = []
        self.trackToSendList = []
           
    # getters
    def getName(self):
        return str(self.name)
    
    def getStatus(self):
        return str(self.status)
    
    def getServerAddress(self):
        return self.server_address
    
    def getNodeTrack(self):
        return self.Node_Track

    # Metodo que adiciona um cliente a uma stream o que significa que o rp tera de enviar 
    # os dados que recebe do servidor desta stream segundo o caminho que definiu como 
    # sendo o melhor 
    def addClient(self, ip_cliente, melhor_caminho):
        print(f"Client {ip_cliente} connectado à Stream {self.name}")
        # Tratar do caso em que é o primeiro cliente a pedir a Stream
        if self.status == "Closed":
            try:
                self.status = "Pending"
                # Adicionar o caminho à lista de caminhos para clientes
                self.trackToClientesList.append(melhor_caminho)

                # atualizar a lista de caminhos para envio
                self.updateTrackToSendList()
                
                # Notificar o servidor que pode enviar esta stream que pode começar a enviar
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
                    try:
                        server_socket.connect(self.server_address)
                
                        msg = f"Start Stream- {self.name}"
                        data = msg.encode('utf-8')
                        dataToSend = (
                            len(data).to_bytes(4, 'big') +
                            data
                        )
                        server_socket.send(dataToSend)
                    except Exception as e:
                        print(f"Erro ao enviar o pedido de stream ao servidor: {e}")
                    finally:
                        server_socket.close()   
                self.status = "Streaming"
            except Exception as e:
                print(f"Erro na adição do primeiro cliente à stream: {e}")
        # Tratar do caso em que ja esta a ser stream ja esta a ser enviada para um outro cliente
        elif self.status == "Streaming":
            try:
                # escolher o caminho mais rapido para o cliente em questao
                # Adicionar o caminho à lista de caminhos para clientes
                self.trackToClientesList.append(melhor_caminho)

                # atualizar a lista de caminhos para envio
                self.updateTrackToSendList()
            except Exception as e:
                print(f"Erro na adição do cliente a stream ja aberta: {e}")

    # Metodo que envia a Stream para os vizinhos necessarios reestroturando o pacote com os dados
    # relativos as conexões e direções para onde o pacote tem de ser enviado
    def sendStream(self, frameNumber, framepart, frame):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as stream_socket:
                try:
                    for track in self.trackToSendList:
                        # Criar o pacote com o caminho ate os cliente
                        pck = Packet(track[1], frameNumber, framepart, frame)
                        dataToSend = pck.buildPacket()
                        send_address = (track[0], self.nodePort)
                        
                        stream_socket.sendto(dataToSend, send_address)
                        #print(f"mensagem frame nº:{pck.frameNumber} send to: {send_address}")
                except Exception as e:
                    print(f"Error sending stream from RP: {e}")
        except Exception as e:
            print(f"Error creating and sending the packet from RP: {e}")

    # Metodo que remove um cliente de assistir à Stream reformulando os caminhos 
    # verificando se o servidro ainda precisa de enviar a Stream
    def rmvClient(self, client_ip):
        try:
            for t in self.trackToClientesList:
                if client_ip in t:
                    self.trackToClientesList.remove(t)
                    if self.trackToClientesList == []: self.status = "Closed"
                    break
            self.updateTrackToSendList()
            # avisar o Server para parar de stremar
            if self.status == "Closed":
                #print(self.server_address)
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socket_server:
                    socket_server.connect(self.server_address)

                    mensagem = f"Stop Stream- {self.name}"
                    data = mensagem.encode('utf-8')
                    dataToSend = (
                        len(data).to_bytes(4, 'big') +
                        data
                    )
                    socket_server.sendall(dataToSend)
                    socket_server.close()
        except Exception as e:
            print("Erro ao remover o caminho para o cliente que deu dsiconnect: ", e)

    # Metodo que atualiza a mensagem a adicionar aos pacotes e o vizinho para onde enviar o primeiro pacote
    # self.trackToSendList = (ip do vizinho para onde enviar , resto do caminho ate ao cliente)
    # para diminuir a complexidade um caminho que era "10.0.1.2 -> 10.0.3.2 | 10.0.3.2 -> 10.0.4.2,10.0.0.5"
    # fica representado como "1.2:3.2|3.2:4.2,0.5"
    def updateTrackToSendList(self):
        try:
            newTrackList = []
            if len(self.trackToClientesList) == 0:
                self.trackToSendList = newTrackList
            elif len(self.trackToClientesList) == 1:
                caminhos_unificado = self.trackToClientesList[0]
            else:
                caminhos_unificado = caminho_combinado(self.trackToClientesList)
            print(f"\nCaminho Unificado: {caminhos_unificado}\n")
            pares = extrair_pares(caminhos_unificado)
            inic = pares.pop(0)

            trackToPacket = ""
            for p in pares:
                trackToPacket += f"{p[0].split('.')[-2]}.{p[0].split('.')[-1]}:"
                ips = p[1].split(",") if "," in p[1] else [p[1]]
                trackToPacket += ",".join([f"{i.split('.')[-2]}.{i.split('.')[-1]}" for i in ips])
                trackToPacket += "|"
            trackToPacket = trackToPacket[:-1]

            ips = inic[1].split(",") if "," in inic[1] else [inic[1]]
            newTrackList.extend([(i, trackToPacket) for i in ips])
            self.trackToSendList = newTrackList
        except Exception as e:
            print("Erro no update da lista de caminhos a adicionar aos pacotes: ", e)
        finally:
            print(f"Lista de nós vizinhos que vão receber a Stream {self.name} alterada")
            for i in self.trackToSendList:
                print(f"\tNó: {i[0]} com mensagem: {i[1]}")

    def updateTrackToClientList(self, client_IP, new_track):
        try:
            for t in self.trackToClientesList:
                if client_IP in t:
                    self.trackToClientesList.remove(t)
                    self.trackToClientesList.append(new_track)
                    self.updateTrackToSendList()
                    break
        except Exception as e:
            print("Erro ao atualizar a lista de clientes na stream: ",e)
        finally:
            print(f"Lista de clientes que vão receber a Stream {self.name} alterada")
            for i in self.trackToClientesList:
                print(f"\tCliente: {i}") 