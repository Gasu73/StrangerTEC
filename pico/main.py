import machine
import time
import network
import socket
 
 

# WIFI

 
SSID     = "KevinNet"
PASSWORD = "12345678"
 
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(SSID, PASSWORD)
 
while not wifi.isconnected():
    pass
 
print("Conectado")
 
direccion_ip = wifi.ifconfig()[0]
print("IP:", direccion_ip)
 
 
 
servidor = socket.socket()
servidor.bind(("0.0.0.0", 5000))
servidor.listen(1)    
 
print("Esperando conexiones en", direccion_ip, ":5000")
 
 

# MAPA DE CARACTERES  (fila, columna)
 
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
 


# TABLA MORSE  código -> letra

 
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
 
 

# TABLA TEXTO -> MORSE  letra -> código
 
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
 
 

# PARÁMETROS DE MORSE
 
UNIDAD_MS = 200
 
DURACION_PUNTO = UNIDAD_MS
DURACION_RAYA  = UNIDAD_MS * 3
 
PAUSA_IMPULSOS = UNIDAD_MS
PAUSA_LETRAS   = UNIDAD_MS * 3

ESPACIO_PALABRAS = UNIDAD_MS * 7
 
 
 
codigo_actual     = ""
mensaje_morse     = ""
tiempo_inicio_btn = 0
ultimo_evento_ms  = time.ticks_ms()
 
 

# PINES
 
AB1  = machine.Pin(14, machine.Pin.OUT)
CLK1 = machine.Pin(15, machine.Pin.OUT)
 
AB2  = machine.Pin(12, machine.Pin.OUT)
CLK2 = machine.Pin(13, machine.Pin.OUT)
 
boton  = machine.Pin(0, machine.Pin.IN, machine.Pin.PULL_UP)
buzzer = machine.PWM(machine.Pin(16))

dip_leds = machine.Pin(2, machine.Pin.IN, machine.Pin.PULL_UP)
dip_buzzer = machine.Pin(3, machine.Pin.IN, machine.Pin.PULL_UP)
 
 

# BITS APAGADOS — estado inicial del display

 
BITS_APAGADOS = [0] * 16
 
enviar_bit_init = True  # bandera para apagar al arrancar

modo_salida = "ninguno"


# LEER ESTADO DEL DIP

def actualizar_modo():

    global modo_salida

    leds_activo = dip_leds.value() == 0
    buzzer_activo = dip_buzzer.value() == 0

    if leds_activo and buzzer_activo:

        modo_salida = "ambos"

    elif leds_activo:

        modo_salida = "leds"

    elif buzzer_activo:

        modo_salida = "buzzer"

    else:

        modo_salida = "ninguno"

    print("Modo:", modo_salida)
 
 

# FUNCIÓN: enviar_bit
 
def enviar_bit(valor):
 
    for i in range(8):
        bit = valor[15 - i]
        AB2(bit)
        CLK2(1)
        CLK2(0)
 
    for i in range(8):
        bit = valor[7 - i]
        AB1(bit)
        CLK1(1)
        CLK1(0)
 
 
# Apagar display al arrancar
enviar_bit(BITS_APAGADOS)
 
 

 
def mostrar_caracter(caracter):
 
    caracter = caracter.upper()
 
    if caracter not in mapa_caracteres:
        print("Caracter no valido:", caracter)
        return
 
    fila, columna = mapa_caracteres[caracter]
 
    bits = [0] * 16
    bits[fila]    = 1
    bits[columna] = 1
 
    enviar_bit(bits)
 
 
# Muestra cada letra en el display con un retardo entre ellas
 
def recorrer_palabra(palabra, tiempo_ms):
 
    for letra in list(palabra):
 
        if letra == " ":
            time.sleep_ms(tiempo_ms)
            continue
 
        mostrar_caracter(letra)
        time.sleep_ms(tiempo_ms)
 
    enviar_bit(BITS_APAGADOS)
 
 

# Emite la frase en morse por el buzzer
 
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
            time.sleep_ms(unidad)       # pausa entre impulsos
 
        time.sleep_ms(unidad * 3)       # pausa entre letras
 
 

# Lee el botón físico y acumula puntos/rayas.
# Decodifica la letra cuando detecta una pausa suficiente.

def leer_morse():
 
    global codigo_actual, mensaje_morse, tiempo_inicio_btn, ultimo_evento_ms
 
    # Botón presionado (PULL_UP: 0 = presionado)
    if boton.value() == 0:
 
        tiempo_inicio_btn = time.ticks_ms()
 
        buzzer.freq(700)
        buzzer.duty_u16(30000)
 
        while boton.value() == 0:
            time.sleep_ms(5)
 
        buzzer.duty_u16(0)
 
        duracion_ms = time.ticks_diff(time.ticks_ms(), tiempo_inicio_btn)
 
        if duracion_ms < DURACION_RAYA:
            codigo_actual += "."
            print(".")
        else:
            codigo_actual += "-"
            print("-")
 
        ultimo_evento_ms = time.ticks_ms()
 
    # Pausa sin actividad
    pausa_actual = time.ticks_diff(time.ticks_ms(), ultimo_evento_ms)
 
    # Fin de letra: pausa >= PAUSA_LETRAS
    if codigo_actual != "" and pausa_actual >= PAUSA_LETRAS:
 
        letra_decodificada = MORSE.get(codigo_actual, "?")
        mensaje_morse     += letra_decodificada
 
        print("Letra:", letra_decodificada)
        print("Mensaje acumulado:", mensaje_morse)
 
        mostrar_caracter(letra_decodificada)
 
        codigo_actual = ""
        ultimo_evento_ms = time.ticks_ms()  # Reinicia para medir el espacio entre palabras
 
    # Espacio entre palabras: pausa >= ESPACIO_PALABRAS
    elif codigo_actual == "" and mensaje_morse != "" and not mensaje_morse.endswith(" ") and pausa_actual >= ESPACIO_PALABRAS:
 
        mensaje_morse += " "
 
        print("Espacio entre palabras")
        print("Mensaje acumulado:", mensaje_morse)
 
        mostrar_caracter(" ")
 
 

# Acepta una conexión entrante y ejecuta el comando.

 
def leer_wifi():
 
    global mensaje_morse, modo_salida
 
    try:
        cliente, direccion_cliente = servidor.accept()
 
    except OSError:
        
        return
 
    print("Cliente conectado desde:", direccion_cliente)
 
    datos_crudos = cliente.recv(1024).decode().strip()
    print("Mensaje recibido:", datos_crudos)
 
    if datos_crudos == "":
        cliente.close()
        return
 
 
    if datos_crudos == "ACTIVAR_MORSE":
 
        mensaje_morse = ""                  # limpiar buffer antes de empezar
        ultimo_evento_ms = time.ticks_ms()  # reiniciar referencia de tiempo
 
        inicio = time.time()
 
        while time.time() - inicio < 20:
            leer_morse()
            time.sleep_ms(10)
 
        # Cerrar la letra en curso si quedó algo sin decodificar
        if codigo_actual != "":
            letra = MORSE.get(codigo_actual, "?")
            mensaje_morse += letra
 
        print("Morse finalizado:", mensaje_morse)
 
        cliente.send(mensaje_morse.strip().encode())
        cliente.close()
 
        mensaje_morse = ""
        return
 
 
    partes = datos_crudos.split("|")
 
    if len(partes) != 3:
        print("modo|texto|velocidad")
        cliente.send(b"ERROR:formato")
        cliente.close()
        return
 
    texto     = partes[1]
    velocidad = int(partes[2])
    
    actualizar_modo()
 
    if modo_salida == "leds":
        recorrer_palabra(texto, velocidad*7)
 
    elif modo_salida == "buzzer":
        transmitir_morse(texto, velocidad)
 
    elif modo_salida == ("ambos"):
        recorrer_palabra(texto, velocidad*7)
        transmitir_morse(texto, velocidad)
        
    cliente.send(b"OK")
    cliente.close()
    

transmitir_morse("I")
 

# LOOP PRINCIPAL

while True:
    leer_wifi()
    time.sleep_ms(10)