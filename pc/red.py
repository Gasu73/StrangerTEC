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

def enviar_a_raspberry(ip, modo, texto, velocidad):
    """
    Abre una conexión TCP hacia la Raspberry, envía el comando
    y espera la confirmación "OK".
    Devuelve True si tuvo éxito, False si hubo error.
    """
    try:
        mensaje = f"{modo}|{texto}|{velocidad}"

        cliente = socket.socket()
        cliente.settimeout(3)
        cliente.connect((ip, PUERTO_RASPBERRY))

        print("Enviando a Raspberry:", repr(mensaje))
        cliente.send(mensaje.encode())

        respuesta = cliente.recv(1024).decode()
        print("Respuesta Raspberry:", respuesta)

        cliente.close()
        return True

    except Exception as error:
        print("Error al enviar a la Raspberry:", error)
        return False


# ---------------------------------------------------------
# SERVIDOR DE ESCUCHA (hilo en segundo plano)
# Recibe la respuesta del jugador B desde la Raspberry.
# La Raspberry envía: "MORSE_B|<mensaje>"
# ---------------------------------------------------------

def _bucle_servidor_escucha():
    """
    Hilo permanente que escucha en PUERTO_ESCUCHA_PC.
    Al recibir un mensaje del tipo "MORSE_B|texto" actualiza
    estado.respuesta_jugador_b para que el hilo de espera
    lo detecte.
    """
    servidor = socket.socket()
    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    servidor.bind(('', PUERTO_ESCUCHA_PC))   # <-- puerto 6000, distinto al de la Raspberry
    servidor.listen(1)
    servidor.settimeout(1)

    print(f"Servidor de escucha activo en puerto {PUERTO_ESCUCHA_PC}")

    while True:
        try:
            cliente, direccion = servidor.accept()
            datos = cliente.recv(1024).decode().strip()
            cliente.close()

            print("Mensaje recibido desde Raspberry:", datos)

            if datos.startswith("MORSE_B|"):
                estado.respuesta_jugador_b = datos.replace("MORSE_B|", "").strip()
                print("Respuesta jugador B:", estado.respuesta_jugador_b)

        except socket.timeout:
            pass   # normal: sin conexión entrante en este ciclo

        except Exception as error:
            print("Error en servidor de escucha:", error)


def iniciar_servidor_escucha():
    """Lanza el hilo de escucha como daemon (se cierra al cerrar la app)."""
    hilo = threading.Thread(target=_bucle_servidor_escucha, daemon=True)
    hilo.start()
