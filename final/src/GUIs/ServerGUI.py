import socket 
import threading
import time
import cv2
from src.Packet import *
from src.NodeData import *

'''
Esta é a classe principal para o Servidor
'''
class ServerGUI:
    def __init__(self, node):
        self.node = node
        self.streamList = {}
        self.serverStarter()

    def serverStarter(self):
        self.conectToRP()
        self.receberPedidos()
    
    # Metodo responsavel por estabelecer a conexão com o RP onde envia a lista das 
    # Streams que é capaz de transmitir
    def conectToRP(self):
        server_address = (NodeData.getIp(self.node),0)
        rp_address = (NodeData.getRPAddress(self.node))
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as rp_socket:
            try:
                rp_socket.bind(server_address)
                rp_socket.connect(rp_address)
        
                # enviar as Streams que tem para exibir
                msg = ""
                for stream in NodeData.getStreamList(self.node).keys():
                    msg += f"{stream}-AND-"

                msg = msg[:-5] 
                data = msg.encode('utf-8')
                dataToSend = (
                    len(data).to_bytes(4, 'big') +
                    data
                )
                rp_socket.sendall(dataToSend)

            except Exception as e:
                print(f"Erro ao conectar ou enviar mensagens: {e}")
            finally:
                print("Server conected to RP")
                rp_socket.close()

    # Metodo responsavel por receber tanto os pedidos de Streams como os pedidos de parar 
    # de Streamar, quando um pedido de stream é recebido é entao iniciada a transmissão
    def receberPedidos(self):
        print("Server waiting Stream requests")
        socket_address = (NodeData.getIp(self.node), 12346)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            try:
                server_socket.bind(socket_address)
                server_socket.listen()
                while True:
                    conn, _ = server_socket.accept()
                    size = conn.recv(4)
                    msg_size = int.from_bytes(size, byteorder='big')

                    msg_data = conn.recv(msg_size)
                    mensagem = msg_data.decode('utf-8')

                    if "Start Stream- " in mensagem:
                        stream_name = extrair_texto(mensagem)
                        self.streamList[stream_name] = "Asked"
                        thread = threading.Thread(target=self.startStream)
                        thread.start()
                    elif "Stop Stream- " in mensagem:
                        stream_to_close = extrair_texto(mensagem)
                        self.closeStream(stream_to_close)
                    else:
                        print(mensagem)
                        
                    conn.close()
            except Exception as e:
                print(f"Erro ao receber mensagens do RP: {e}")
            finally:
                server_socket.close()

    # Metodo responsavel por iniciar a transmissão de um stream via socket UDP para o RP
    # cada frame de video é fracionado em 3 pacotes 
    # cada pacote é contituido por (tamanho total + 
    #                               tamanho do nome em bytes +
    #                               nome em bytes + 
    #                               numero do frame +
    #                               tamanho da fração de frame +
    #                               fração de frame em bytes)
    # esta definido tambem um controlo de 25 frames por segundo para garantir o frame_rate
    # na visualização
    def startStream(self):
        streamName = None
        for s in self.streamList.keys():
            if self.streamList[s] == "Asked":
                streamName = s
        self.streamList[streamName] = "Streaming"
        print(f"Streaming: {streamName}")

        streampath = NodeData.getStreamList(self.node)[streamName]
        rp_address = (NodeData.getRPAddress(self.node)[0], NodeData.getStreamPort(self.node))
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as stream_socket:
            try:
                # Abrir a stream através do caminho para a mesma
                sstream = cv2.VideoCapture(streampath)
                fps =  sstream.get(cv2.CAP_PROP_FPS)
                # Controlo do Frama_rate
                frame_interval = 1.0 / fps
                st = time.time()
                # Numeração dos frames
                i=0
                # Transmitir enquanto houver stream e tiver clientes a assitir
                while sstream.isOpened() and self.streamList[streamName] != "Closed":
                    # Leitura de frame a frame
                    ret, frame = sstream.read()
                    if not ret:break

                    # Resize dos frames e passar para bytes
                    Frame = cv2.resize(frame, (FRAME_WIDTH, FRAME_HEIGHT))
                    frame_data = cv2.imencode('.jpg', Frame)[1].tobytes()
                    
                    # Obtenha o comprimento total dos dados e dicidir por 2 partes identicas
                    total_length = len(frame_data)
                    split_point1 = total_length // 2
                    
                    data_part1 = frame_data[:split_point1]
                    data_part2 = frame_data[split_point1:]
                   
                    # Construir os 2 pacotes e envia-los para o RP
                    pacote = Packet(streamName, i, 1, data_part1)
                    pacote_data = pacote.buildPacket()
                    stream_socket.sendto(pacote_data, rp_address)
                    pacote = Packet(streamName, i, 2, data_part2)
                    pacote_data = pacote.buildPacket()
                    stream_socket.sendto(pacote_data, rp_address)
                    
                    # Controlo do Frama_rate
                    elapsed_time = time.time() - st
                    time.sleep(max(0, frame_interval - elapsed_time))
                    st = time.time()

                    #print("Frame: ",i)
                    i+=1
                # Controlo quando o video acaba e consequentemente termina a Stream
                if self.streamList[streamName] == "Streaming":
                    self.streamList[streamName] = "Asked"
                    self.startStream()

            except Exception as e:
                print(f"Erro ao Streamar para o RP: {e}")
            finally:
                stream_socket.close()

    # Metodo responsavel por parar de Transmitir quando assim pedido pelo RP
    def closeStream(self, stream):
        self.streamList[stream] = "Closed"
        print(f"{stream} closed!")
