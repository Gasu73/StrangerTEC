import json
import os
from datetime import datetime

from constantes import MORSE, MORSE_INVERSO, ARCHIVO_TOP10




def texto_a_morse(texto):
    """
    Convierte una cadena de texto a su representación Morse.
    Los espacios entre palabras se representan con '/'.
    Ejemplo: "SOS" -> "...  ---  ..."
    """
    partes = []

    for caracter in texto.upper():
        if caracter in MORSE:
            partes.append(MORSE[caracter])
        elif caracter == ' ':
            partes.append('/')

    return '  '.join(partes)


def morse_a_texto(secuencia_morse):
    """
    Convierte una secuencia Morse a texto.
    Los '/' representan espacios entre palabras.
    """
    resultado = ''

    for parte in secuencia_morse.strip().split(' '):
        if parte == '/':
            resultado += ' '
        elif parte:
            resultado += MORSE_INVERSO.get(parte, '?')

    return resultado




def calcular_puntaje(frase_original, frase_recibida):
    """
    Compara la frase original con la recibida carácter a carácter
    (sin espacios, en mayúsculas).

    Devuelve la tupla:
        (letras_correctas, total_letras, porcentaje)
    """
    original = frase_original.upper().replace(' ', '')
    recibida = frase_recibida.upper().replace(' ', '')

    letras_correctas = sum(
        1
        for i in range(min(len(original), len(recibida)))
        if original[i] == recibida[i]
    )

    total_letras = len(original)

    if total_letras > 0:
        porcentaje = int(letras_correctas / total_letras * 100)
    else:
        porcentaje = 0

    return letras_correctas, total_letras, porcentaje




def top10_cargar():
    """Lee el archivo JSON del Top 10. Devuelve lista vacía si no existe."""
    if os.path.exists(ARCHIVO_TOP10):
        try:
            return json.load(open(ARCHIVO_TOP10, encoding='utf-8'))
        except Exception:
            pass
    return []


def top10_guardar(lista):
    """Guarda los primeros 10 registros en el archivo JSON."""
    json.dump(
        lista[:10],
        open(ARCHIVO_TOP10, 'w', encoding='utf-8'),
        indent=2,
        ensure_ascii=False
    )


def top10_agregar_entrada(nombre, puntos, modo):
    """
    Agrega una entrada al Top 10, reordena por puntos y guarda.
    Devuelve la posición (1-10) del jugador en la tabla,
    o None si no entró al top 10.
    """
    tabla = top10_cargar()

    nueva_entrada = {
        'nombre': nombre[:12].upper(),
        'puntos': puntos,
        'modo':   modo,
        'fecha':  datetime.now().strftime('%d/%m/%y'),
    }

    tabla.append(nueva_entrada)
    tabla.sort(key=lambda entrada: entrada['puntos'], reverse=True)
    top10_guardar(tabla)

    for posicion, entrada in enumerate(tabla[:10]):
        if entrada['nombre'] == nombre[:12].upper() and entrada['puntos'] == puntos:
            return posicion + 1

    return None
