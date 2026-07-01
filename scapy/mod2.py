import socket, time, base64

SERVIDOR = "172.18.0.2"
PUERTO = 5222
USUARIO = "usuario1"
PASSWORD = "clave_prueba"

STREAM = b"<?xml version='1.0'?><stream:stream to='localhost' xmlns='jabber:client' xmlns:stream='http://etherx.jabber.org/streams' version='1.0'>"

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((SERVIDOR, PUERTO))
sock.settimeout(3)

def enviar(data):
    sock.send(data)

def recibir():
    time.sleep(2)
    try:
        return sock.recv(65535)
    except:
        return b''

enviar(STREAM)
recibir()

auth = base64.b64encode(f"\x00{USUARIO}\x00{PASSWORD}".encode()).decode()
enviar(f"<auth xmlns='urn:ietf:params:xml:ns:xmpp-sasl' mechanism='PLAIN'>{auth}</auth>".encode())
resp = recibir()

if b'success' in resp:
    print("[*] Autenticado correctamente")
    enviar(STREAM)
    recibir()

    enviar(b"<iq type='set' id='bind1'><bind xmlns='urn:ietf:params:xml:ns:xmpp-bind'><resource>scapy</resource></bind></iq>")
    resp = recibir()
    print(f"[*] Bind: {resp[:100]}")

    enviar(b"<presence/>")
    recibir()

    payload = b"<message to='usuarioinexistente@localhost' type='chat'><body>hola</body></message>"
    enviar(payload)
    print(f"[+] Mensaje enviado a usuario inexistente")
    time.sleep(5)
    resp = recibir()
    print(f"[*] Respuesta: {resp[:200] if resp else 'sin respuesta'}")
else:
    print("[!] Autenticacion fallida")

sock.close()
