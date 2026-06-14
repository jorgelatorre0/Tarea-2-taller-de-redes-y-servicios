# Tarea 2 - Taller de Redes y Servicios
## Protocolo XMPP

##Video de demostración

[Ver video](https://drive.google.com/file/d/1a4GxtvX7xx5B5dluu6hbPquAjpsAY7gG/view?usp=sharing)

Implementación de una arquitectura cliente-servidor usando el protocolo XMPP, con ejabberd como servidor y Profanity como cliente, ambos compilados desde su código fuente oficial y ejecutados en contenedores Docker independientes.

## Tecnologías utilizadas

- **Servidor:** [ejabberd](https://github.com/processone/ejabberd)
- **Cliente:** [Profanity](https://github.com/profanity-im/profanity)
- **Contenedorización:** Docker
- **Análisis de tráfico:** Wireshark

## Requisitos previos

- Docker instalado
- Wireshark instalado

## Instrucciones de uso

### 1. Compilar las imágenes

```bash
sudo docker build -f Dockerfile.servidor -t servidor-xmpp .
sudo docker build -f Dockerfile.cliente -t cliente-xmpp .
```

### 2. Crear la red Docker compartida

```bash
sudo docker network create red-xmpp
```

### 3. Levantar el servidor

```bash
sudo docker run -d -p 5222:5222 -p 5280:5280 --hostname localhost --name servidor-xmpp --network red-xmpp servidor-xmpp
```

### 4. Editar la configuración TLS del servidor

El certificado del servidor es autofirmado, por lo que es necesario desactivar TLS para permitir la conexión del cliente:

```bash
sudo docker cp servidor-xmpp:/usr/local/etc/ejabberd/ejabberd.yml ./ejabberd.yml
sudo chmod 644 ./ejabberd.yml
sed -i 's/starttls_required: true/starttls_required: false/' ./ejabberd.yml
sudo docker cp ./ejabberd.yml servidor-xmpp:/usr/local/etc/ejabberd/ejabberd.yml
sudo docker exec servidor-xmpp ejabberdctl restart
```

### 5. Registrar un usuario

```bash
sudo docker exec servidor-xmpp ejabberdctl register tarea2 localhost clave_prueba
```

### 6. Levantar el cliente

```bash
sudo docker run -it -e TERM=xterm --name cliente-xmpp --network red-xmpp cliente-xmpp
```

### 7. Conectarse desde Profanity

Dentro de Profanity ejecutar (contraseña: clave_prueba):

```bash
/connect tarea2@localhost server servidor-xmpp tls disable
```

### 8. Análisis de tráfico con Wireshark

Para capturar el tráfico XMPP entre cliente y servidor:

1. Identificar la interfaz de red Docker:

```bash
ip link show
```

Buscar la interfaz que comienza con `br-`, que corresponde a la red `red-xmpp`.

2. Abrir Wireshark y seleccionar la interfaz `br-xxxxxxx`.

3. Aplicar el filtro:

```bash
xmpp
```
4. Iniciar la captura y conectarse desde Profanity. Se podrán observar las siguientes fases del protocolo:
- STREAM: apertura del flujo XML entre cliente y servidor
- AUTH / CHALLENGE / RESPONSE / SUCCESS: fase de autenticación SASL
- BIND: enlace del recurso del cliente al servidor
- PRESENCE: anuncio de disponibilidad del cliente
- QUERY disco#info / disco#items: descubrimiento de servicios del servidor

## Autores

- Bastián Ampuero
- Jorge Latorre

