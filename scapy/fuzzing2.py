from scapy.all import *
from scapy.supersocket import StreamSocket
import socket
import time
import base64
import random
import string

SERVIDOR = "172.18.0.2"
PUERTO = 5222
USUARIO = "usuario1"
PASSWORD = "clave_prueba"

def random_string(length=10):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

payloads = [
    f"<iq type='{random_string()}' id='{random_string()}'><query xmlns='{random_string()}'/></iq>".encode(),
    f"<iq type='set' id='{random_string()}'><bind xmlns='urn:ietf:params:xml:ns:xmpp-bind'><resource>{'X' * 5000}</resource></bind></iq>".encode(),
    f"<iq type='get' id='{random_string()}' to='{'A' * 1000}@localhost'><query xmlns='jabber:iq:roster'/></iq>".encode(),
    b"<iq>" * 100 + b"</iq>" * 100,
    f"<iq type='set' id='{random_string()}'><query xmlns='jabber:iq:auth'><username>{random_string()}</username><password>{random_string()}</password></query></iq>".encode(),
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

ss = StreamSocket(raw_sock, Raw)

ss.send(Raw(load=b"<?xml version='1.0'?><stream:stream to='localhost' xmlns='jabber:client' xmlns:stream='http://etherx.jabber.org/streams' version='1.0'>"))
recibir(ss)

auth_b64 = base64.b64encode(f"\x00{USUARIO}\x00{PASSWORD}".encode()).decode()
ss.send(Raw(load=f"<auth xmlns='urn:ietf:params:xml:ns:xmpp-sasl' mechanism='PLAIN'>{auth_b64}</auth>".encode()))
resp = recibir(ss)

if b'success' in resp:
    print("[*] Autenticado correctamente")
    ss.send(Raw(load=b"<?xml version='1.0'?><stream:stream to='localhost' xmlns='jabber:client' xmlns:stream='http://etherx.jabber.org/streams' version='1.0'>"))
    recibir(ss)

    print("[*] Iniciando fuzzing de stanzas IQ con paquetes Scapy...")
    for i, payload in enumerate(payloads):
        try:
            pkt = Raw(load=payload)
            ss.send(pkt)
            print(f"[+] Stanza IQ {i+1} enviada: {payload[:80]}...")
            resp = recibir(ss)
            print(f"[*] Respuesta: {resp[:150]}" if resp else "[*] Sin respuesta del servidor")
        except Exception as e:
            print(f"[!] Error en stanza {i+1}: {e}")
        time.sleep(1)
else:
    print("[!] Autenticación fallida")

ss.close()
print("[*] Fuzzing completado.")
