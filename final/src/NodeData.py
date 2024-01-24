from src.auxiliarFunc import *

'''
Esta é a classe principal para a esrutura de dados usada para todas as interfaces do sistema
Para cada componente na rede existe informação sobre ele no ficheiro de configuração que é 
utilizada para a construção desta estrutura 
'''
class NodeData:
    def __init__(self, ip , file):
        self.IP = ip
        self.type = None
        self.node_port = None
        self.stream_port = None
        self.ident = None
        self.neighbours_address = []
        self.RP_address = None
        self.PORTACLIENT = None
        self.PORTASERVER = None
        self.stream_list = {}
        self.parse_file(file)
        
    # Getters
    def getIp(self):
        return str(self.IP)
    
    def getType(self):
        return str(self.type)
    
    def getNodePort(self):
        return int(self.node_port)
    
    def getStreamPort(self):
        return int(self.stream_port)
    
    def getIdent(self):
        return str(self.ident)
    
    def getNeighboursAddress(self):
        return list(self.neighbours_address)
    
    def getRPAddress(self):
        return (str(self.RP_address[0]), int(self.RP_address[1]))
    
    def getPortaClient(self):
        return int(self.PORTACLIENT)
    
    def getPortaServer(self):
        return int(self.PORTASERVER)
    
    def getStreamList(self):
        return self.stream_list
            
    # Setters
    def setIp(self, ip):
        self.Ip = ip

    def setType(self, type):
        self.type = type

    def setNodePort(self, porta):
        self.node_port = porta

    def setStreamPort(self, porta):
        self.stream_port = porta
    
    def setIdent(self, ident):
        self.ident = ident
    
    def setNeighboursAddress(self, neigh):
        self.neighbours_address.append(neigh)

    def setRPAddress(self, rp):
        self.RP_address = rp

    def setPortaClient(self, pclient):
        self.PORTACLIENT = pclient

    def setPortaServer(self, pserver):
        self.PORTASERVER = pserver

    def setStreamList(self, stream):
        self.stream_list[getVideoName(stream)] = stream

    # Metodo capaz de extrair do ficehiro de configuração a informação relacionada à estrutura em questão
    def parse_file(self, filepath):
        try:
            with open(filepath, 'r') as f:
                readComunData = True
                read = False
                for line in f:
                    if "---common information---" in line:
                        readComunData = True
                    if readComunData:
                        if "nodePort- " in line:
                            self.setNodePort(extrair_numero(line))
                        elif "streamPort- " in line:
                            self.setStreamPort(extrair_numero(line))
                        elif "ident- " in line:
                            self.setIdent(extrair_texto(line))
                        elif "------" in line:
                            readComunData = False
                    if f"ip- {self.IP}" in line:
                        read = True
                    if read:
                        if "type- " in line:
                            self.setType(extrair_texto(line))
                        elif "neighbour- " in line:
                            self.setNeighboursAddress(extrair_texto(line))
                        elif "rp- " in line:
                            self.setRPAddress(extrair_texto_numero(line))
                        elif "portaClient- " in line:
                            self.setPortaClient(extrair_numero(line))
                        elif "portaServer- " in line:
                            self.setPortaServer(extrair_numero(line))
                        elif "stream- " in line:
                            self.setStreamList(extrair_texto(line))
                        elif "------" in line:
                            return
        except FileNotFoundError:
            print(f"Error: File '{filepath}' not found.")
        except Exception as e:
            print(f"An error occurred during parsing: {str(e)}")

    # Metodo de auxilio na visualização e precessão da estrutura
    def tostring(self):
        print("-----------------------------------------------")
        print("IP: " + self.IP)
        print("Tipo: " + self.type)
        if self.node_port:
            print("Porta para Nós: "+ str(self.node_port))
        if self.stream_port:
            print("Porta para Streams: "+ str(self.stream_port))
        for i in self.neighbours_address:
            print("Nó Adjacente: " + i)
        if self.RP_address:
            print("IP do rp: " + str(self.RP_address))
        if self.PORTACLIENT:
            print("Porta Client: " + str(self.PORTACLIENT))
        if self.PORTASERVER:
            print("Porta Server: " + str(self.PORTASERVER))
        for i in self.stream_list:
            print("Streams: " + str(i))
        print("-----------------------------------------------")