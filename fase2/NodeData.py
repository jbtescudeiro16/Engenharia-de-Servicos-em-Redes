from auxiliarFunc import *

class NodeData:

    def __init__(self, ip , file):
        self.IP = ip
        self.type = None
        self.porta_escuta = None
        self.neighbours_address = []
        self.RP_address = None
        self.PORTACLIENT = None
        self.PORTASERVER = None
        self.stream_list = []
        self.parse_file(file)
        
    # Getters
    def getIp(self):
        return str(self.IP)
    
    def getType(self):
        return str(self.type)
    
    def getPortaEscuta(self):
        return int(self.porta_escuta)
    
    def getNeighboursAddress(self):
        return list(self.neighbours_address)
    
    def getRPAddress(self):
        return (str(self.RP_address[0]), int(self.RP_address[1]))
    
    def getPortaClient(self):
        return int(self.PORTACLIENT)
    
    def getPortaServer(self):
        return int(self.PORTASERVER)
    
    def getStreamList(self):
        return list(self.stream_list)
            
    # Setters
    def setIp(self, ip):
        self.Ip = ip

    def setType(self, type):
        self.type = type

    def setPortaEscuta(self, porta):
        self.porta_escuta = porta

    def setNeighboursAddress(self, neigh):
        self.neighbours_address.append(neigh)

    def setRPAddress(self, rp):
        self.RP_address = rp

    def setPortaClient(self, pclient):
        self.PORTACLIENT = pclient

    def setPortaServer(self, pserver):
        self.PORTASERVER = pserver

    def setStreamList(self, stream):
        self.stream_list.append(stream)

    # Function to parse the config file
    def parse_file(self, filepath):
        print("Parsing...")
        try:
            with open(filepath, 'r') as f:
                read = False
                for line in f:
                    if f"ip- {self.IP}" in line:
                        read = True
                    if read:
                        if "type- " in line:
                            self.setType(extrair_texto(line))
                        elif "nodePort- " in line:
                            self.setPortaEscuta(extrair_numero(line))
                        elif "neighbour- " in line:
                            self.setNeighboursAddress(extrair_texto_numero(line))
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

    # Function to verify the info of the node
    def tostring(self):
        print("-----------------------------------------------")
        print("IP: " + self.IP)
        print("Tipo: " + self.type)
        print("Porta_Escuta: "+ str(self.porta_escuta))
        for i in self.neighbours_address:
            print("Nó Adjacente: " + i)
        print("IP do rp: " + self.RP_address)
        print("Porta Client: " + str(self.PORTACLIENT))
        print("Porta Server: " + str(self.PORTASERVER))
        for i in self.stream_list:
            print("Streams: " + i)
        print("-----------------------------------------------")
