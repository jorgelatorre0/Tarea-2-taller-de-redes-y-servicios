from scapy.all import *
from scapy.supersocket import StreamSocket
import socket
import time
import base64

SERVIDOR = "172.18.0.2"
PUERTO = 5222
USUARIO = "usuario1"
PASSWORD = "clave_prueba"

payloads = [
    b"<message to='usuario2@localhost' type='chat'><body>" + b"A" * 10000 + b"</body></message>",
    b"<message to='usuario2@localhost' type='chat'><body><<<<<>>>></body></message>",
    b"<message to='usuario2@localhost' type='chat'><body>\x00\x01\x02\x03</body></message>",
    b"<message to='usuario2@localhost' type='chat'><body><?xml version='2.0'?></body></message>",
    b"<message to='usuario2@localhost' type='chat'><body><![CDATA[<script>alert(1)</script>]]></body></message>",
    b"<message to='usuario2@localhost' type='chat'><body>" + "\U0001F600".encode() * 1000 + b"</body></message>",
]

def recibir(ss, espera=1):
    time.sleep(espera)
    try:
        pkt = ss.recv()
        return bytes(pkt) if pkt else b''
    except:
        return b''

print("[*] Creando socket TCP base...")
raw_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
raw_sock.connect((SERVIDOR, PUERTO))
raw_sock.settimeout(2)

# Envolvemos el socket TCP en un StreamSocket de Scapy
# para construir y enviar las estrofas como paquetes Scapy (Raw layer)
ss = StreamSocket(raw_sock, Raw)

print("[*] Enviando apertura de stream XMPP (Scapy Raw packet)...")
ss.send(Raw(load=b"<?xml version='1.0'?><stream:stream to='localhost' xmlns='jabber:client' xmlns:stream='http://etherx.jabber.org/streams' version='1.0'>"))
print(f"[*] Stream: {recibir(ss)[:150]}")

auth_b64 = base64.b64encode(f"\x00{USUARIO}\x00{PASSWORD}".encode()).decode()
ss.send(Raw(load=f"<auth xmlns='urn:ietf:params:xml:ns:xmpp-sasl' mechanism='PLAIN'>{auth_b64}</auth>".encode()))
resp = recibir(ss)
print(f"[*] Auth: {resp[:150]}")

if b'success' in resp:
    print("[*] Autenticado correctamente")
    ss.send(Raw(load=b"<?xml version='1.0'?><stream:stream to='localhost' xmlns='jabber:client' xmlns:stream='http://etherx.jabber.org/streams' version='1.0'>"))
    recibir(ss)

    print("[*] Iniciando fuzzing con paquetes Scapy...")
    for i, payload in enumerate(payloads):
        try:
            pkt = Raw(load=payload)
            ss.send(pkt)
            print(f"[+] Payload {i+1} enviado ({len(payload)} bytes): {payload[:80]}...")
            resp = recibir(ss)
            print(f"[*] Respuesta: {resp[:150]}" if resp else "[*] Sin respuesta del servidor")
        except Exception as e:
            print(f"[!] Error en payload {i+1}: {e}")
        time.sleep(1)
else:
    print("[!] Autenticación fallida")

ss.close()
print("[*] Fuzzing completado.")
