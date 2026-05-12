import machine
import time
import network
import socket
import _thread
 
 
# =========================================================
# WIFI
# =========================================================
 
SSID     = "AP_50196"
PASSWORD = "ivonne2023"
 
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(SSID, PASSWORD)
 
while not wifi.isconnected():
    pass
 
print("Conectado")
 
direccion_ip = wifi.ifconfig()[0]
 
print("IP:", direccion_ip)
 
 
# =========================================================
# SERVIDOR SOCKET (modo no-bloqueante)
# =========================================================
 
servidor = socket.socket()
servidor.bind((direccion_ip, 5000))
servidor.listen(1)

 
print("Esperando conexiones en", direccion_ip, ":5000")
 
 
# =========================================================
# MAPA DE CARACTERES  (fila, columna del display)
# =========================================================
 
mapa_caracteres = {
 
    # FILA 2
    'A': (2, 3),  'C': (2, 4),  'E': (2, 5),  'G': (2, 6),
    'I': (2, 7),  'K': (2, 8),  'M': (2, 9),  'O': (2, 10),
    'Q': (2, 11), 'S': (2, 12), 'U': (2, 13), 'W': (2, 14),
    'Y': (2, 15),
 
    # FILA 1
    'B': (1, 3),  'D': (1, 4),  'F': (1, 5),  'H': (1, 6),
    'J': (1, 7),  'L': (1, 8),  'N': (1, 9),  'P': (1, 10),
    'R': (1, 11), 'T': (1, 12), 'V': (1, 13), 'X': (1, 14),
    'Z': (1, 15),
 
    # FILA 0
    '0': (0, 3),  '1': (0, 4),  '2': (0, 5),  '3': (0, 6),
    '4': (0, 7),  '5': (0, 8),  '6': (0, 9),  '7': (0, 10),
    '8': (0, 11), '9': (0, 12), '-': (0, 13), '+': (0, 14),
}
 
 
# =========================================================
# TABLA MORSE  (código -> letra)
# =========================================================
 
MORSE = {
    ".-":   "A", "-...": "B", "-.-.": "C", "-..":  "D",
    ".":    "E", "..-.": "F", "--.":  "G", "....": "H",
    "..":   "I", ".---": "J", "-.-":  "K", ".-..": "L",
    "--":   "M", "-.":   "N", "---":  "O", ".--.": "P",
    "--.-": "Q", ".-.":  "R", "...":  "S", "-":    "T",
    "..-":  "U", "...-": "V", ".--":  "W", "-..-": "X",
    "-.--": "Y", "--..": "Z",
 
    ".----": "1", "..---": "2", "...--": "3",
    "....-": "4", ".....": "5", "-....": "6",
    "--...": "7", "---..": "8", "----.": "9",
    "-----": "0",
 
    ".-.-.":  "+",
    "-....-": "-",
}
 
 
# =========================================================
# TABLA TEXTO -> MORSE  (letra -> código)
# =========================================================
 
TEXTO_A_MORSE = {
    "A": ".-",   "B": "-...", "C": "-.-.", "D": "-..",
    "E": ".",    "F": "..-.", "G": "--.",  "H": "....",
    "I": "..",   "J": ".---", "K": "-.-",  "L": ".-..",
    "M": "--",   "N": "-.",   "O": "---",  "P": ".--.",
    "Q": "--.-", "R": ".-.",  "S": "...",  "T": "-",
    "U": "..-",  "V": "...-", "W": ".--",  "X": "-..-",
    "Y": "-.--", "Z": "--..",
 
    "1": ".----", "2": "..---", "3": "...--",
    "4": "....-", "5": ".....", "6": "-....",
    "7": "--...", "8": "---..", "9": "----.",
    "0": "-----",
 
    "+": ".-.-.", "-": "-....-",
}
 
 
# =========================================================
# PARÁMETROS DE MORSE
# =========================================================
 
UNIDAD_MS = 200          # duración de un punto en milisegundos
 
DURACION_PUNTO   = UNIDAD_MS
DURACION_RAYA    = UNIDAD_MS * 3
 
PAUSA_IMPULSOS   = UNIDAD_MS        # entre punto y punto dentro de una letra
PAUSA_LETRAS     = UNIDAD_MS * 3    # entre letras
PAUSA_PALABRAS   = UNIDAD_MS * 7    # entre palabras
 
 
# =========================================================
# ESTADO DEL DECODIFICADOR MORSE (botón físico)
# =========================================================
 
codigo_actual     = ""   # impulsos acumulados de la letra en curso
mensaje_morse     = ""   # mensaje completo decodificado
tiempo_inicio_btn = 0    # marca cuando se presionó el botón
ultimo_evento_ms  = time.ticks_ms()  # última vez que hubo actividad
 
 
# =========================================================
# PINES
# =========================================================
 
# Registro de desplazamiento — cadena 1
AB1  = machine.Pin(14, machine.Pin.OUT)
CLK1 = machine.Pin(15, machine.Pin.OUT)
 
# Registro de desplazamiento — cadena 2
AB2  = machine.Pin(12, machine.Pin.OUT)
CLK2 = machine.Pin(13, machine.Pin.OUT)
 
# NOTA: GPIO0 tiene comportamiento especial durante el boot en ESP8266.
# Si el botón causa reinicios inesperados, cambia a otro pin (ej. GPIO2).
boton  = machine.Pin(0, machine.Pin.IN, machine.Pin.PULL_UP)
 
buzzer = machine.PWM(machine.Pin(16))
 
 
# =========================================================
# BITS EN APAGADO (todos los LEDs apagados)
# =========================================================
 
BITS_APAGADOS = [0] * 16
 
 
# =========================================================
# FUNCIÓN: enviar_bit
# Envía 16 bits a los dos registros de desplazamiento
# =========================================================
 
def enviar_bit(valor):
 
    # Primeros 8 bits -> registro 2 (bits 15..8)
    for i in range(8):
        bit = valor[15 - i]
        AB2(bit)
        CLK2(1)
        CLK2(0)
 
    # Segundos 8 bits -> registro 1 (bits 7..0)
    for i in range(8):
        bit = valor[7 - i]
        AB1(bit)
        CLK1(1)
        CLK1(0)
 
 
# =========================================================
# FUNCIÓN: mostrar_caracter
# Activa la fila y columna del carácter en el display
# =========================================================
 
def mostrar_caracter(caracter):
 
    caracter = caracter.upper()
 
    if caracter not in mapa_caracteres:
        print("Carácter no válido:", caracter)
        return
 
    fila, columna = mapa_caracteres[caracter]
 
    bits = [0] * 16
    bits[fila]    = 1
    bits[columna] = 1
 
    enviar_bit(bits)
 
 
# =========================================================
# FUNCIÓN: recorrer_palabra
# Muestra cada letra de una palabra en el display
# =========================================================
 
def recorrer_palabra(palabra, tiempo_ms):
 
    for letra in list(palabra):
 
        if letra == " ":
            time.sleep_ms(tiempo_ms)
            continue
 
        mostrar_caracter(letra)
        time.sleep_ms(tiempo_ms)
 
    enviar_bit(BITS_APAGADOS)
 
 
# =========================================================
# FUNCIÓN: transmitir_morse
# Convierte texto a morse y lo emite por el buzzer
# =========================================================
 
def transmitir_morse(texto, unidad=200):
 
    texto = texto.upper()
 
    for caracter in texto:
 
        if caracter == " ":
            time.sleep_ms(unidad * 7)
            continue
 
        if caracter not in TEXTO_A_MORSE:
            continue
 
        codigo = TEXTO_A_MORSE[caracter]
        print(caracter, "=", codigo)
 
        for simbolo in codigo:
 
            buzzer.freq(700)
            buzzer.duty_u16(30000)
 
            if simbolo == ".":
                time.sleep_ms(unidad)
 
            elif simbolo == "-":
                time.sleep_ms(unidad * 3)
 
            buzzer.duty_u16(0)
            time.sleep_ms(unidad)   # pausa entre impulsos
 
        time.sleep_ms(unidad * 3)   # pausa entre letras
 
 
# =========================================================
# FUNCIÓN: leer_wifi
# Acepta una conexión entrante y ejecuta el comando recibido.
# El formato esperado es:  modo|texto|velocidad
# Modos válidos: "led", "morse", "ambos"
#
# CORRECCIÓN: servidor en modo no-bloqueante, por eso se
# captura OSError cuando no hay cliente esperando.
# =========================================================
 
def leer_wifi():
    #AGREGAR EL WHILE TRUE
    while True:
        
        try:
            
            cliente, direccion_cliente = servidor.accept()
            print("Cliente conectado desde:", direccion_cliente)
         
            datos_crudos = cliente.recv(1024).decode().strip()
            print("Mensaje recibido:", datos_crudos)
         
            if datos_crudos == "":
                cliente.close()
                return
         
            partes = datos_crudos.split("|")
         
            if len(partes) != 3:
                print("Formato inválido — se esperaba: modo|texto|velocidad")
                cliente.send(b"ERROR:formato")
                cliente.close()
                return
         
            modo      = partes[0]
            texto     = partes[1]
            velocidad = int(partes[2])
         
            # =========================================================
            # FUNCIÓN: enviar_mensaje_morse
            # Envía el mensaje morse acumulado de vuelta al cliente PC.
            # Se llama cuando el jugador B termina de ingresar su respuesta.
            # =========================================================
         
            # Responder al cliente que el comando fue recibido
            cliente.send(b"OK")
            cliente.close()
         
            # Ejecutar según el modo
            if modo == "led":
                recorrer_palabra(texto, velocidad)
         
            elif modo == "morse":
                transmitir_morse(texto, velocidad)
         
            elif modo == "ambos":
                recorrer_palabra(texto, velocidad)
                transmitir_morse(texto, velocidad)
            
        except:

            pass
 
 
# =========================================================
# FUNCIÓN: enviar_mensaje_morse_al_pc
# Abre una conexión TCP hacia la PC para enviar el mensaje
# que el jugador B tecleó en morse.
# ip_pc y puerto_pc deben configurarse con los datos reales.
# =========================================================
 
 
 # Se asigna cuando la PC se conecta por primera vez
puerto_pc = 6000   # Puerto donde la PC escucha respuestas
 
def enviar_mensaje_morse_al_pc(mensaje_a_enviar):
 
    try:
        cliente_saliente = socket.socket()
        cliente_saliente.connect(("192.168.100.12", puerto_pc))
        cliente_saliente.send(("MORSE_B|" + mensaje_a_enviar).encode())
        cliente_saliente.close()
        print("Mensaje enviado a la PC:", mensaje_a_enviar)
 
    except Exception as error:
        
        print("Error al enviar a la PC:", error)
 
 
# =========================================================
# FUNCIÓN: leer_morse
# Lee el botón físico, acumula puntos/rayas y decodifica
# la letra cuando se detecta una pausa suficiente.
# Al completar una palabra la envía a la PC.
# =========================================================
 
def leer_morse():
 
    global codigo_actual, mensaje_morse, tiempo_inicio_btn, ultimo_evento_ms
 
    # ---------------------------------------------------------
    # BOTÓN PRESIONADO
    # ---------------------------------------------------------
    if boton.value() == 0:
 
        tiempo_inicio_btn = time.ticks_ms()
 
        buzzer.freq(700)
        buzzer.duty_u16(30000)
 
        # Esperar a que se suelte el botón
        while boton.value() == 0:
            pass
 
        buzzer.duty_u16(0)
 
        duracion_ms = time.ticks_diff(time.ticks_ms(), tiempo_inicio_btn)
 
        if duracion_ms < DURACION_RAYA:
            codigo_actual += "."
            print(".")
        else:
            codigo_actual += "-"
            print("-")
 
        ultimo_evento_ms = time.ticks_ms()
 
    # ---------------------------------------------------------
    # CALCULAR CUÁNTO TIEMPO LLEVA SIN ACTIVIDAD
    # ---------------------------------------------------------
    pausa_actual = time.ticks_diff(time.ticks_ms(), ultimo_evento_ms)
 
    # ---------------------------------------------------------
    # FIN DE LETRA: pausa >= 3 unidades
    # ---------------------------------------------------------
    if codigo_actual != "" and pausa_actual >= PAUSA_LETRAS:
 
        letra_decodificada = MORSE.get(codigo_actual, "?")
        mensaje_morse     += letra_decodificada
 
        print("Letra:", letra_decodificada)
        print("Mensaje acumulado:", mensaje_morse)
 
        mostrar_caracter(letra_decodificada)
 
        codigo_actual = ""
 
    # ---------------------------------------------------------
    # FIN DE PALABRA: pausa >= 7 unidades
    # Al detectar fin de palabra, se envía el mensaje a la PC
    # ---------------------------------------------------------
    if pausa_actual >= PAUSA_PALABRAS:
 
        if mensaje_morse != "" and not mensaje_morse.endswith(" "):
 
            mensaje_morse += " "
            print("Mensaje (con espacio):", mensaje_morse)
 
            # Enviar el mensaje morse completado a la PC
            # (la PC lo usará como respuesta del jugador B)
            
            enviar_mensaje_morse_al_pc(mensaje_morse.strip())
            
            
            

 
 
# =========================================================
# LOOP PRINCIPAL
# =========================================================
_thread.start_new_thread(leer_wifi,())

while True:
    leer_morse()    # siempre se ejecuta
    time.sleep_ms(10)