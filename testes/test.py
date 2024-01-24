def extrair_conexoes(lista, input_string):
    #lista de tuplos (endereço para enviar, caminho a partir daí)
    try:
        if "|" in input_string:
            partes = input_string.split(' | ',1)
            conexao = partes[0].split(" -> ")
            if "," in conexao[1]:
                ips = conexao[1].split(",")
                for i in ips:
                    if i in partes[1]:
                        lista.append((i, partes[1]))
            else:
                if conexao[1] in  partes[1]:
                    lista.append((conexao[1], partes[1]))
        else:
            conexao = input_string.split(" -> ")
            if "," in conexao[1]:
                ips = conexao[1].split(",")
                for i in ips:
                    lista.append((i,""))
            else:
                lista.append((conexao[1],""))
    except Exception as e:
        print("Erro ao criar a lista de tuplos",e)
    
def possibelToMerge(caminho, Node_Track):
    pares_str1 = extrair_pares(caminho)
    count=0
    for i in Node_Track:
        pares_str2 = extrair_pares(i[1])
        for par1 in pares_str1:
            for par2 in pares_str2:
                if par1 == par2:
                    return count
        count+=1
    return None  

def extrair_pares(input_string):
        if "|" in input_string:
            parts = input_string.split(' | ')
            return [tuple(part.split(" -> ")) for part in parts]
        else:
            return [tuple(input_string.split(" -> "))]

def combinar_caminhos(caminho1, caminho2):
    pares_str1 = extrair_pares(caminho1)
    pares_str2 = extrair_pares(caminho2)
    conexoes_dict = {}
    for par in pares_str1:
        if par[0] not in conexoes_dict:
            conexoes_dict[par[0]] = par[1]
        if par[1] not in conexoes_dict[par[0]]:
            aux = conexoes_dict[par[0]]
            conexoes_dict[par[0]] = aux + "," + par[1] 

    for par in pares_str2:
        if par[0] not in conexoes_dict:
            conexoes_dict[par[0]] = par[1]
        if par[1] not in conexoes_dict[par[0]]:
            aux = conexoes_dict[par[0]]
            conexoes_dict[par[0]] = aux + "," + par[1] 

    partes = []
    for inicio, fins in conexoes_dict.items():
        partes.append(f"{inicio} -> {fins}")
    return ' | '.join(partes)

# Exemplo de uso
# 127.0.0.1 -> 127.0.0.3 | 127.0.0.3 -> 127.0.0.4 | 127.0.0.4 -> 127.0.0.5
# ficar (127.0.0.3, 127.0.0.3 -> 127.0.0.4 | 127.0.0.4 -> 127.0.0.5)
# depois (127.0.0.4, 127.0.0.4 -> 127.0.0.5)
# depois (127.0.0.5, "")

lista = []
caminho = "127.0.0.1 -> 127.0.0.3 | 127.0.0.3 -> 127.0.0.4 | 127.0.0.4 -> 127.0.0.5"
extrair_conexoes(lista, caminho)
print(lista)
caminho = lista.pop()
lista = []
extrair_conexoes(lista, caminho[1])
print(lista)
caminho = lista.pop()
lista = []
extrair_conexoes(lista, caminho[1])
print(lista)

# merge 
# 127.0.0.1 -> 127.0.0.3 | 127.0.0.3 -> 127.0.0.4 | 127.0.0.4 -> 127.0.0.5
# com # 127.0.0.1 -> 127.0.0.3 | 127.0.0.3 -> 127.0.0.4 | 127.0.0.4 -> 127.0.0.6
# ficar (127.0.0.3, 127.0.0.3 -> 127.0.0.7 | 127.0.0.4 -> 127.0.0.5,127.0.0.6
# depois (127.0.0.4, 127.0.0.4 -> 127.0.0.5,127.0.0.6)
# depois (127.0.0.5, "") e (127.0.0.6, "")

caminho1 = "127.0.0.1 -> 127.0.0.3 | 127.0.0.3 -> 127.0.0.4 | 127.0.0.4 -> 127.0.0.5"
caminho2 = "127.0.0.1 -> 127.0.0.3 | 127.0.0.3 -> 127.0.0.4 | 127.0.0.4 -> 127.0.0.6"

caminho = combinar_caminhos(caminho1, caminho2)
lista = []
extrair_conexoes(lista, caminho)
print(lista)
caminho = lista.pop()
lista = []
extrair_conexoes(lista, caminho[1])
print(lista)
caminho = lista.pop()
lista = []
extrair_conexoes(lista, caminho[1])
print(lista)


