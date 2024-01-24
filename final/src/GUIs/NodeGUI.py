import threading
import socket
from src.NodeData import *
from src.Packet import *

'''
Esta é a classe principal para o Node
'''
class NodeGUI:
    def __init__(self, node):
        self.node = node
        self.streamConnection()
 
    #-----------------------------------------------------------------------------------------
    # Receber de Streams e enviar
    def streamConnection(self):
        my_address = (NodeData.getIp(self.node), NodeData.getStreamPort(self.node))
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as socketForStream:
            try:
                socketForStream.bind(my_address)
                print(f"{my_address} waiting for Streams")
                i=0
                while True:
                    #parse packet
                    data, _ = socketForStream.recvfrom(Packet_size)
                    i+=1
                    
                    pck = Packet("", "", "", "")
                    pck.parsePacket(data)
                    caminhos = extrair_conexoes(NodeData.getIp(self.node), NodeData.getIdent(self.node), pck.info)
                   
                    #e enviar para todos os clientes
                    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as stream_socket:
                        try:
                            for nei in caminhos:
                                print(f"pacote enviado do: {NodeData.getIp(self.node)} para: {nei} pacote nª: {pck.frameNumber}")
                                send_address = (nei, NodeData.getStreamPort(self.node))
                                stream_socket.sendto(data, send_address)
                        except Exception as e:
                            print(f"Error sending stream from Node {NodeData.getIp(self.node)}: {e}")
                        finally:
                            stream_socket.close()                   
            except Exception as e:
                print(f"Erro no streaming no Nó {NodeData.getIp(self.node)}: {e}")
            finally:
                socketForStream.close()