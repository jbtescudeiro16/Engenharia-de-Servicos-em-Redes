from PIL import Image, ImageTk
import cv2, imutils, socket
import numpy as np
import time, os
import base64
import threading, wave, pyaudio,pickle,struct
import tkinter as tk

class Cliente():
	def __init__(self):
		self.janela = tk.Tk()
		self.janela.title("Cliente")
        
        # Substitui o Canvas por um Label
		self.label = tk.Label(self.janela, width=640, height=480, bg='white')
		self.label.pack()

		self.botaoClose = tk.Button(self.janela, width=20, padx=3, pady=3)
		self.botaoClose["text"] = "Close"
		self.botaoClose.pack(padx=2, pady=2)

		self.host_ip = "127.0.0.1"
		self.porta = 12345
		self.BUFF_SIZE = 65536
		self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.BREAK = False
		self.receive_video = True
		self.photo = None

		self.main()

	def receive_video_thread(self):
		while self.receive_video:
			try:
				# Recebe o tamanho do frame (4 bytes) do servidor
				frame_size_bytes = self.server_socket.recv(4)
				frame_size = int.from_bytes(frame_size_bytes, byteorder='big')

				# Recebe o frame do servidor
				frame_data = b""
				while len(frame_data) < frame_size:
					frame_data += self.server_socket.recv(frame_size - len(frame_data))

				# Converte os dados do frame em uma imagem
				img = ImageTk.PhotoImage(data=frame_data)

				# Atualiza a label na janela Tkinter com a nova imagem
				self.label.configure(image=img)
				self.label.image = img
				self.janela.update()
			except Exception as e:
                # Registre a exceção para fins de depuração
				print(f"Erro ao receber vídeo: {e}")
		
	def recibeAudio(self):
		p = pyaudio.PyAudio()
		CHUNK = 1024
		stream = p.open(format=p.get_format_from_width(2),
						channels=2,
						rate=44100,
						output=True,
						frames_per_buffer=CHUNK)
						
		# create socket
		client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		socket_address = (self.host_ip,self.porta-1)
		print('server listening at',socket_address)
		client_socket.connect(socket_address) 
		print("CLIENT CONNECTED TO",socket_address)
		data = b""
		payload_size = struct.calcsize("Q")
		while True:
			try:
				while len(data) < payload_size:
					packet = client_socket.recv(4*1024) # 4K
					if not packet: break
					data+=packet
				packed_msg_size = data[:payload_size]
				data = data[payload_size:]
				msg_size = struct.unpack("Q",packed_msg_size)[0]
				while len(data) < msg_size:
					data += client_socket.recv(4*1024)
				frame_data = data[:msg_size]
				data  = data[msg_size:]
				frame = pickle.loads(frame_data)
				stream.write(frame)
			except:
				break
		client_socket.close()
		print('Audio closed',self.BREAK)
		os._exit(1)

	def initialCon(self):
		socket_address = (self.host_ip, self.porta)
		self.server_socket.connect(socket_address)
		print("Cliente connectado: ", socket_address)

	def main(self):
		self.initialCon()
		t1 = threading.Thread(target=self.receive_video_thread)
		t2 = threading.Thread(target=self.recibeAudio)
		t1.start()
		t2.start()
		self.janela.mainloop()
		

if __name__ == "__main__":
    cliente = Cliente()
    cliente.janela.mainloop()

'''def unified_stream(self):
    s = socket.socket()
    new_address = (self.IP, (self.porta-1))
    s.bind(new_address)

    s.listen(5)
    CHUNK = 1024
    wf = wave.open(self.audiofile, 'rb')
    p = pyaudio.PyAudio()
    print('server listening at',new_address)
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    input=True,
                    frames_per_buffer=CHUNK)
    client_socket,addr = s.accept()
    while True:
        if client_socket:
            while True:
                # Video Frame
                ret, frame = self.vid.read()
                if not ret:
                    break

                frame = cv2.resize(frame, (FRAME_WIDTH, FRAME_HEIGHT))
                frame_data = cv2.imencode('.jpg', frame)[1].tobytes()

                # Audio Frame
                data = wf.readframes(CHUNK)
                a = pickle.dumps(data)
                audio_data = struct.pack("Q",len(a))+a

                # Send both video and audio frame size
                message = struct.pack("Q", len(frame_data)) + frame_data + struct.pack("Q", len(audio_data)) + audio_data
                client_socket.sendall(message)

                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    os._exit(1)
                    self.TS = False
                    break

    print('Player closed')
    self.BREAK = True
    self.vid.release()
    wf.close()
    stream.stop_stream()
    stream.close()
    p.terminate()'''

'''import numpy as np
import socket
import sys
import struct
import pyaudio

def main():
    ip = "127.0.0.1" # Endereço IP do servidor
    port = 55555 # Porta do servidor

    # Configuração do socket UDP
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_address = (ip, port)

    # Inicializa o PyAudio
    audio = pyaudio.PyAudio()

    # Inicializa o objeto Stream para reprodução de áudio
    stream = audio.open(format=pyaudio.paInt16,
                        channels=1,
                        rate=44100,
                        output=True)

    try:
        print('Esperando mensagens UDP no endereço', server_address)
        while True:
            # Recebe os dados UDP
            data, server = sock.recvfrom(4096)

            # Lê o tamanho do frame de áudio
            audio_size = struct.unpack("Q", data[:8])[0]

            # Lê o frame de áudio em si
            audio_data = data[8:8+audio_size]

            # Converte o frame de áudio para int16
            audio_frame = np.frombuffer(audio_data, dtype=np.int16)

            # Escreve o frame de áudio no objeto Stream
            stream.write(audio_frame.tobytes())

    except KeyboardInterrupt:
        print('Fechando a conexão...')
        stream.stop_stream()
        stream.close()
        audio.terminate()
        sock.close()
        sys.exit(0)

if __name__ == '__main__':
    main()'''