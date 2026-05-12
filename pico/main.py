import machine
import time
import sys


# =========================================================
# MAPA DE CARACTERES
# =========================================================

mapa_caracteres = {

    # FILA 2
    'A': (2, 3),
    'C': (2, 4),
    'E': (2, 5),
    'G': (2, 6),
    'I': (2, 7),
    'K': (2, 8),
    'M': (2, 9),
    'O': (2, 10),
    'Q': (2, 11),
    'S': (2, 12),
    'U': (2, 13),
    'W': (2, 14),
    'Y': (2, 15),

    # FILA 1
    'B': (1, 3),
    'D': (1, 4),
    'F': (1, 5),
    'H': (1, 6),
    'J': (1, 7),
    'L': (1, 8),
    'N': (1, 9),
    'P': (1, 10),
    'R': (1, 11),
    'T': (1, 12),
    'V': (1, 13),
    'X': (1, 14),
    'Z': (1, 15),

    # FILA 0
    '0': (0, 3),
    '1': (0, 4),
    '2': (0, 5),
    '3': (0, 6),
    '4': (0, 7),
    '5': (0, 8),
    '6': (0, 9),
    '7': (0, 10),
    '8': (0, 11),
    '9': (0, 12),
    '-': (0, 13),
    '+': (0, 14),
}


# =========================================================
# PINES
# =========================================================

AB1 = machine.Pin(14, machine.Pin.OUT)
CLK1 = machine.Pin(15, machine.Pin.OUT)

AB2 = machine.Pin(12, machine.Pin.OUT)
CLK2 = machine.Pin(13, machine.Pin.OUT)

boton = machine.Pin(0, machine.Pin.IN, machine.Pin.PULL_UP)
buzzer = machine.PWM(machine.Pin(16))

#boton y buzzer

while True:

    if boton.value() == 0:
        buzzer.freq(700)
        buzzer.duty_u16(30000)
        print("Hola")

    else:
        buzzer.duty_u16(0)

    time.sleep_ms(10)



# FUNCIÓN PARA ENVIAR UN BIT
def enviar_bit(valor):
    for i in range(8):  
        bit = valor[15-i]  # tomar los valores de derecha a izquiera
        AB2(bit)      
        CLK2(1)                          
        CLK2(0)

    for i in range(8):  
        bit = valor[7-i]  # tomar los valores de derecha a izquiera
        AB1(bit)      
        CLK1(1)                          
        CLK1(0)

    
# FUNCIÓN Generar la secuencia
def ejecutar_secuencia(caracter):

    caracter = caracter.upper()

    if caracter not in mapa_caracteres:
        print("Carácter no válido")
        return

    fila, columna = mapa_caracteres[caracter]

    print("Carácter:", caracter)
    print("Fila:", fila)
    print("Columna:", columna)

    # Crear 16 bits apagados
    bits = [0] * 16

    # Encender fila y columna
    bits[fila] = 1
    bits[columna] = 1

    print(bits)
    enviar_bit(bits) # Enviar todos los bits

    
#funcion Descomponer palabras
def recorrer_palabra(palabra, tiempo_ms):

    letras = list(palabra)

    for letra in letras:

        ejecutar_secuencia(letra)

        time.sleep_ms(tiempo_ms)

    enviar_bit([0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])








