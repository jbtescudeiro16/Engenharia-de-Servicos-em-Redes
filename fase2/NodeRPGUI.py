import socket
from auxiliarFunc import *
from NodeData import *
import threading

class NodeRPGUI:

    def __init__(self, node):
        self.janela = None
        self.node = node
        self.caminhos = []
        self.start()

    def start(self):
        print("Starting...")

        thread0 = threading.Thread(target=self.recieveConnection)
        thread0.start()

    def recieveConnection(self):
        print("Recieving...")

        socket_address = (NodeData.getIp(self.node), NodeData.getPortaEscuta(self.node))

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind(socket_address)
            server_socket.listen()
            server_socket.settimeout(30)  # 1 min de escuta

            while True:
                try:
                    client_connection, client_address = server_socket.accept()
                    client_connection.settimeout(60)  # Defina o timeout para o recebimento de dados

                    size = client_connection.recv(4)
                    msg_size = int.from_bytes(size, byteorder='big')

                    msg = b""
                    while len(msg) < msg_size:
                        msg += client_connection.recv(msg_size - len(msg))

                    mensagem = msg.decode('utf-8')
                    print(mensagem)
                    self.caminhos.append(mensagem)

                except socket.timeout:
                    print(f"Nenhum cliente conectou-se ao Node {NodeData.getIp(self.node)} dentro do tempo limite. Parando a receção de conexões.")
                    break
                except Exception as e:
                    print(f"Erro na receção de conexões no Nodo {NodeData.getIp(self.node)}")

    def printCaminhos(self):
        for caminho in self.caminhos:
            print(caminho)