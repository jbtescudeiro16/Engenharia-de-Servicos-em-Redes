import os, re

'''
Metodos auxiliares que são usados pelas diferentes estruturas
'''

# Metodo que retorna o nome do video quando lhe é passado o caminho para o mesmo
def getVideoName(video):
    nomeExtensao = os.path.basename(video)
    video_sem_extensao, _ = os.path.splitext(nomeExtensao)
    return video_sem_extensao

# Metodo que retorna um inteiro seguido de um " - "
def extrair_numero(texto):
    padrao = r'[a-z]*-\s*(\d+)'
    correspondencia = re.search(padrao, texto)
    numero_porta = correspondencia.group(1)
    return int(numero_porta)

# Metodo que retorna a string seguida de um " - "
def extrair_texto(texto):
    padrao = r'[a-z_]*- ([\w.\/]+)'
    correspondencia = re.search(padrao, texto)
    return correspondencia.group(1)

# Metodo que retorna um tuplo com uma string e um inteiro seguida de um " - " e separados por um " - "
def extrair_texto_numero(texto):
    padrao = r'[a-z_]*- ([\w.\/]+)\s+-\s+(\d+)'
    correspondencia = re.search(padrao, texto)
    return (correspondencia.group(1), int(correspondencia.group(2)))

# Metodo inverte uma conexão para ser usada na ordem certa pelo RP
def inverter_relacoes(mensagens):
    if "|" in mensagens:
        relacoes = mensagens.split(' | ')
        mensagens_invertidas = ""
        while relacoes:
            conn = relacoes.pop()
            conn = invert_ip_addresses(conn)
            mensagens_invertidas += conn + " | "
            
        mensagens_invertidas = mensagens_invertidas[:-3] 
    else:
        mensagens_invertidas = invert_ip_addresses(mensagens)
    return mensagens_invertidas

def invert_ip_addresses(address_string):
    addresses = address_string.split('<-')
    inverted_address = f"{addresses[1].strip()} -> {addresses[0].strip()}"
    return inverted_address

# Metodo que devolve a lista de nodos vizinhos para quem tem de enviar o pacote
def extrair_conexoes(ip, ident, input_string):
    try:
        ip_terminação = f"{ip.split('.')[-2]}.{ip.split('.')[-1]}"
        send_list = []
        if "|" in input_string:
            partes = input_string.split('|')
            for p in partes:
                send_recv = p.split(":")
                if ip_terminação in send_recv[0]:
                    if "," in send_recv[1]:
                        ips = send_recv[1].split(",")
                        for i in ips:
                            send_list.append(f"{ident}{i}")
                    else:
                        send_list.append(f"{ident}{send_recv[1]}")
        else:
            send_recv = input_string.split(":")
            if ip_terminação in send_recv[0]:
                if "," in send_recv[1]:
                    ips = send_recv[1].split(",")
                    for i in ips:
                        send_list.append(f"{ident}{i}")
                else:
                    send_list.append(f"{ident}{send_recv[1]}")
        return send_list
    except Exception as e:
        print("Erro ao criar a lista de tuplos",e)
    
# Metodo auxiliar que separa as conexões em pares
def extrair_pares(input_string):
        if "|" in input_string:
            parts = input_string.split(' | ')
            return [tuple(part.split(" -> ")) for part in parts]
        else:
            return [tuple(input_string.split(" -> "))]

# Metodo que combina os dois caminhos que podem ser unificados num só caminho
def caminho_combinado(lista):
    conexoes_dict = {}
    ends = []
    for caminho in lista:
        pares_str1 = extrair_pares(caminho)
        for pares in pares_str1:
            if not conexoes_dict.get(pares[0]):
                conexoes_dict[pares[0]] = pares[1]
                ends.append(pares[1])
            else:
                p = conexoes_dict[pares[0]] 
                if pares[1] not in p and pares[1] not in ends:
                    conexoes_dict[pares[0]] = f"{p},{pares[1]}"
                    ends.append(pares[1])
    partes = []
    for inicio, fins in conexoes_dict.items():
        partes.append(f"{inicio} -> {fins}")
    return ' | '.join(partes)

# Metodo que separa o caminho do timestamp de um caminho enviado por um cliente
def getTrackAndTimeAndUpdateNumber(caminho):
    partes = caminho.split(" :clst- ")
    partes2 = partes[1].split(" :n- ")
    return (partes[0], float(partes2[0]), int(partes2[1]))

# Metodo que devolve o ip do cliente de para um determinado caminho
def getClientIP(caminho):
    pares = extrair_pares(caminho)
    return pares[-1][1]