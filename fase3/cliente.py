from ClienteGUI import *
import tkinter as Tk


if __name__ == "__main__":
    try:
        ip = '127.0.0.3'
        portaClient = 12345
        ip_rp = '127.0.0.1'
    except Exception as e:
        print(f"Erro: {e}")
        print("[Usage: Cliente.py]\n")
    
     # Criar um cliente
    janela = Tk()
    cliente = ClienteGUI(janela, ip, ip_rp)
    cliente.janela.title("Servidor")
    janela.mainloop()