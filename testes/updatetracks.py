c = "10.0.8.2 -> 10.0.1.1 | 10.0.1.1 -> 10.0.0.21"
c1 = "10.0.8.2 -> 10.0.13.2 | 10.0.13.2 -> 10.0.11.2 | 10.0.11.2 -> 10.0.20.21"
c2 = "10.0.8.2 -> 10.0.13.2 | 10.0.13.2 -> 10.0.11.2 | 10.0.11.2 -> 10.0.1.1 | 10.0.1.1 -> 10.0.0.20"

cs = []
cs.append(c)
cs.append(c1)
cs.append(c2) 

def updateTrackToSendList(caminhos):
    # Ver se é possivel unificar os caminhos para os varios clientes e atualizar os 
    # os caminhos para enviar 
    caminhos_unificado = caminho_combinado(caminhos)
    newTrackList = []
    
    print(f"\n Caminho Unificado: {caminhos_unificado}\n\n")
    #for c in caminhos_unificados:
    pares = extrair_pares(caminhos_unificado)
    inic = pares.pop(0)
    trackToPacket = ""
    for p in pares:
        trackToPacket += f"{p[0].split('.')[-2]}.{p[0].split('.')[-1]}:"
        if "," in p[1]:
            ips = p[1].split(",")
            for i in ips:
                trackToPacket += f"{i.split('.')[-2]}.{i.split('.')[-1]},"
            trackToPacket = trackToPacket[:-1]
        else:
            trackToPacket += f"{p[1].split('.')[-2]}.{p[1].split('.')[-1]}"
        trackToPacket += "|"
    trackToPacket = trackToPacket[:-1]
    newTrackList.append((inic[1],trackToPacket))
    return newTrackList

def extrair_pares(input_string):
    if "|" in input_string:
        parts = input_string.split(' | ')
        return [tuple(part.split(" -> ")) for part in parts]
    else:
        return [tuple(input_string.split(" -> "))]

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

print(updateTrackToSendList(cs))