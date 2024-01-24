from NodeGUI import NodeGUI
from NodeRPGUI import NodeRPGUI
from NodeData import NodeData

if __name__ == "__main__":
    try:
        # Obtém o endereço IP local da máquina
        ip = input("IP da maquina atual: ")
        filename = "config_file.txt"
        nodedata = NodeData(ip, filename)
        nodedata.tostring()
        if nodedata.getType() == "RendezvousPoint":
            node = NodeRPGUI(nodedata)
        else:
            node = NodeGUI(nodedata)

    except Exception as e:
        print(f'Ocorreu um erro: {str(e)}')