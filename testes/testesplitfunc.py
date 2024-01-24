caminho1 = "127.0.0.1 -> 127.0.0.3 | 127.0.0.3 -> 127.0.0.4 | 127.0.0.4 -> 127.0.0.5"
caminho2 = "127.0.0.1 -> 127.0.0.3 | 127.0.0.3 -> 127.0.0.4 | 127.0.0.4 -> 127.0.0.5,127.0.0.6"

ip = "127.0.0.5"

def splitTracks(track, client_ip):
    partes = track.split(" | ")
    last = partes.pop()
    if "," in last:
        conn = last.split(" -> ")
        ips = conn[1].split(",")
        novos_ips = f"{conn[0]} -> "
        novos_ips += ",".join(ip for ip in ips if ip != client_ip)

        partes.append(novos_ips)
        return ' | '.join(partes)
    return None

print(splitTracks(caminho1, ip))
print(splitTracks(caminho2, ip))