from time import sleep
from src.NodeData import NodeData
from src.GUIs.NodeOverlayGUI import NodeOverlayGUI
from src.GUIs.NodeGUI import NodeGUI
from src.GUIs.RPGUI import RPGUI
from src.GUIs.ClienteGUI import ClienteGUI
from src.GUIs.ServerGUI import ServerGUI
import os
import tkinter as tk

'''
Este é o metodo que é executado e apenas é necessario indicar qual o ip da estrutura em questao
e ele ira chamar a Nodedata para retirar do ficheiro de configuração a informação que a ele 
corresponde e depois consuante o tipo de estrutura que é executada de acordo com esse tipo
'''
if __name__ == "__main__":
    try:
        # Obtém o endereço IP local da máquina
        ip = input("IP da maquina atual: ")
        filename = "config_file.txt"

        nodedata = NodeData(ip, filename)
        nodedata.tostring()
        
        if nodedata.getType() == "RendezvousPoint":
            os.environ["DISPLAY"] = ":0.0"
            rp = RPGUI(nodedata)
        else:
            node = NodeOverlayGUI(nodedata)
            if nodedata.getType() == "Client":
                sleep(5)
                os.environ["DISPLAY"] = ":0.0"
                janela = tk.Tk()
                cliente = ClienteGUI(janela, nodedata)
                janela.mainloop()
            elif nodedata.getType() == "Server":
                sleep(3)
                servidor = ServerGUI(nodedata)
            elif nodedata.getType() == "Node":
                node = NodeGUI(nodedata)

    except Exception as e:
        print(f'Ocorreu um erro: {str(e)}')