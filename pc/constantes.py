# ---------------------------------------------------------
# CONFIGURACIÓN DEL JUEGO
# ---------------------------------------------------------

MAXIMAS_RONDAS  = 3
ARCHIVO_TOP10   = 'top10.json'

# Puerto donde la Raspberry Pi escucha comandos de la PC
PUERTO_RASPBERRY = 5000


PUERTO_ESCUCHA_PC = 6000

FRASES_PREDETERMINADAS = [
    'SOS', 'SI', 'NO', 'HOLA', 'TEC',
    'MORSE', 'PICO', 'WIFI', 'STRANGER', 'UPSIDE DOWN',
]


# ---------------------------------------------------------
# COLORES
# ---------------------------------------------------------

COLOR_FONDO        = '#111111'
COLOR_TEXTO        = '#e8e8e8'
COLOR_ROJO         = '#cc2222'
COLOR_GRIS         = '#666666'
COLOR_VERDE        = '#44cc44'
COLOR_FONDO_OSCURO = '#1a1a1a'


# ---------------------------------------------------------
# FUENTES
# ---------------------------------------------------------

FUENTE_TITULO  = ('Courier New', 28, 'bold')
FUENTE_GRANDE  = ('Courier New', 16, 'bold')
FUENTE_MEDIANA = ('Courier New', 14)
FUENTE_NORMAL  = ('Courier New', 12)
FUENTE_PEQUEÑA = ('Courier New', 10)


# Tabla morse

MORSE = {
    'A': '.-',    'B': '-...', 'C': '-.-.', 'D': '-..',
    'E': '.',     'F': '..-.', 'G': '--.',  'H': '....',
    'I': '..',    'J': '.---', 'K': '-.-',  'L': '.-..',
    'M': '--',    'N': '-.',   'O': '---',  'P': '.--.',
    'Q': '--.-',  'R': '.-.',  'S': '...',  'T': '-',
    'U': '..-',   'V': '...-', 'W': '.--',  'X': '-..-',
    'Y': '-.--',  'Z': '--..',
    '0': '-----', '1': '.----', '2': '..---',
    '3': '...--', '4': '....-', '5': '.....',
    '6': '-....', '7': '--...',  '8': '---..',
    '9': '----.',
    '+': '.-.-.', '-': '-....-',
}

# Tabla inversa: código -> letra
MORSE_INVERSO = {codigo: letra for letra, codigo in MORSE.items()}
