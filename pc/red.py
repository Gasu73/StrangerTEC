# =========================================================
# red.py
# Comunicación TCP con la Raspberry Pi.
#
# La PC actúa como CLIENTE para enviar comandos (puerto 5000)
# y como SERVIDOR para recibir la respuesta del jugador B
# que llega desde la Raspberry (puerto 6000).
# =========================================================

import socket
import threading

import estado
from constantes import PUERTO_RASPBERRY, PUERTO_ESCUCHA_PC


# ---------------------------------------------------------
# ENVIAR COMANDO A LA RASPBERRY
# Formato del mensaje:  modo|texto|velocidad
# Modos válidos: "led", "morse", "ambos"
# ---------------------------------------------------------

def enviar_a_raspberry(ip, modo, velocidad=None):
    
    try:
        cliente = socket.socket()
 
        if modo == 'ACTIVAR_MORSE':
            # La Raspberry tarda hasta 20 s en responder
            cliente.settimeout(25)
            mensaje = 'ACTIVAR_MORSE'
        else:
            cliente.settimeout(5)
            mensaje = f"{modo}|{estado.frase_actual}|{velocidad}"
 
        cliente.connect((ip, PUERTO_RASPBERRY))
 
        print("Enviando a Raspberry:", repr(mensaje))
        cliente.send(mensaje.encode())
 
        respuesta = cliente.recv(1024).decode().strip()
        print("Respuesta Raspberry:", respuesta)
 
        cliente.close()
 
        if modo == 'ACTIVAR_MORSE':
            return respuesta        # texto decodificado en morse por el botón
        else:
            return True
 
    except Exception as error:
        print("Error al enviar a la Raspberry:", error)
        if modo == 'ACTIVAR_MORSE':
            return ''
        else:
            return False


