import os, re

def getVideoName(video):
    # nome do ficheiro sem o caminho
    nomeExtensao = os.path.basename(video)
    video_sem_extensao, extensao = os.path.splitext(nomeExtensao)
    return video_sem_extensao

def extrair_numero_porta(texto):
    padrao = r'[a-z]*-\s*(\d+)'
    correspondencia = re.search(padrao, texto)
    numero_porta = correspondencia.group(1)
    return int(numero_porta)

def extrair_conteudo(texto):
    padrao = r'[a-z_]*- ([\w.\/]+)'
    correspondencia = re.search(padrao, texto)
    return correspondencia.group(1)

def extrair_neighbour(texto):
    padrao = r'[a-z_]*- ([\w.\/]+)\s+-\s+(\d+)'
    correspondencia = re.search(padrao, texto)
    return (correspondencia.group(1), int(correspondencia.group(2)))
