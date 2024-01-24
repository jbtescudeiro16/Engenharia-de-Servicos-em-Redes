from src.NodeData import *
import threading
import socket
import time

'''
Esta é a classe principal para o NodeOverlay
Todas as estruturas sao um Nodo Overlay e nesta classe é tratada a conexão dos mesmos e assegurada
a manutenção da rede
'''
class NodeOverlayGUI:
    def __init__(self, node):
        self.node = node
        self.status = "Closed" # |"Open"
        self.condition = threading.Condition()
        self.conditionBool = False
        self.networkUpdateNumber = -1
        self.start()

    # Abre a receção de conexoes com os seus vizinhos e espera a rede ser estabelicida uma vez
    # para que possa avançar para iniciar as funçoes relativas a cada estrutura
    def start(self):
        thread0 = threading.Thread(target=self.recieveConnection)
        thread0.start()
        #espera a conexao inicial
        with self.condition:
            while not self.conditionBool:
                self.condition.wait()
        self.conditionBool = False

    # Recebe e trata as conexoes com os vizinhos
    def recieveConnection(self):
        socket_address = (NodeData.getIp(self.node), NodeData.getNodePort(self.node))
        print(f"{NodeData.getIp(self.node)} waiting for Node connections")
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
                server_socket.bind(socket_address)
                server_socket.listen()
                # Recebe todo o tipo de conexões dos seus vizinhos
                while True:
                    client_connection, _ = server_socket.accept()
            
                    size = client_connection.recv(4)
                    msg_size = int.from_bytes(size, byteorder='big')

                    msg_data = client_connection.recv(msg_size)
                    mensagem = msg_data.decode('utf-8')

                    if self.status == "Closed" and "Update Network-" in mensagem:
                        self.status = "Open"
                        self.processUpdateNetwork(mensagem)
                        with self.condition:
                            self.conditionBool = True
                            self.condition.notify()
                    elif self.status == "Open":
                        if "Update Network" in mensagem:
                            self.processUpdateNetwork(mensagem)
                        # Trata de adicionar a sua posição ao caminho de um vizinho ate ao rp
                        elif NodeData.getIp(self.node) not in mensagem:
                                mensagem = mensagem + " <- " + NodeData.getIp(self.node) + " | " + NodeData.getIp(self.node)
                                self.sendMessageToAdjacentNodes(mensagem)
                    # Caso o seu IP esteja na mensagem não ira voltar a enviar essa mensagem para evitar loops infinitos  
                    client_connection.close()
        except Exception as e:
            print(f"Erro na receção de conexões no Nodo {NodeData.getIp(self.node)}")
        finally:
            server_socket.close()

    '''Se for uma mensagem de update network é pq o RP pediu uma atualização da rede
    e entao tenho de enviar essa mensagem para os vizinhos para que eles recebam essa informação
    para além disso ele envia uma mensagem com o seu ip para os seus vizinhos com o objetivo de
    essa mensagem chegar ao RP com o respetivo caminho (nodo ate ao RP)'''
    def processUpdateNetwork(self, mensagem):
        try:
            # enviar o pedido de update Network se coressponder a um novo pedido do RP
            update_number = extrair_numero(mensagem)
            if update_number > self.networkUpdateNumber:
                self.networkUpdateNumber = update_number
                self.sendMessageToAdjacentNodes(mensagem)
                # enviar o ip para os vizinhos para que o caminho do nó ate ao RP chegue ao mesmo
                # Se for um cliente enviamos ainda o timeStamp atual para que possa ser usa na 
                # metrica de escolha do caminho optimo no rp
                if NodeData.getType(self.node) == "Client":
                    st_time = time.time()
                    firstConMsg = f"{NodeData.getIp(self.node)} :clst- {st_time} :n- {self.networkUpdateNumber}"
                else:
                    firstConMsg = NodeData.getIp(self.node)
                self.sendMessageToAdjacentNodes(firstConMsg)
        except Exception as e:
            print("Erro ao processar a mensagem de Update Network: ",e)

    # Metodo que envia determinada mensagem para todos os nodos vizinhos 
    def sendMessageToAdjacentNodes(self, mensagem):
        for adj in NodeData.getNeighboursAddress(self.node): 
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.connect((adj, NodeData.getNodePort(self.node)))
                    data = mensagem.encode('utf-8')
                    msg = (
                        len(data).to_bytes(4, 'big') +
                        data
                    )
                    s.sendall(msg)
                except Exception as e:
                    print(f"Não foi possível enviar mensagem para {adj}:{str(e)}")
                finally:
                    s.close()
