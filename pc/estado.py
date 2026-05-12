# =========================================================
# estado.py
# Variables globales que representan el estado del juego.
# Se importan y modifican desde pantallas.py y red.py.
# =========================================================

from constantes import FRASES_PREDETERMINADAS

# ---------------------------------------------------------
# CONEXIÓN
# ---------------------------------------------------------

ip_raspberry = ''       # IP que el usuario ingresa en pantalla de conexión

# ---------------------------------------------------------
# PARTIDA
# ---------------------------------------------------------

modo_juego   = 1        # 1 = Transmisión Simple  /  2 = Escucha y Transmisión
nivel_juego  = 1        # Multiplicador de puntos (se puede ampliar a futuro)

nombre_jugador_a = 'JUGADOR A'
nombre_jugador_b = 'JUGADOR B'

puntos_jugador_a = 0
puntos_jugador_b = 0

ronda_actual  = 0
frase_actual  = ''
turno_actual  = 'A'     # 'A' = turno del jugador A  /  'B' = turno del jugador B

respuesta_guardada_a = ''   # Respuesta de A mientras se espera la de B

lista_frases = list(FRASES_PREDETERMINADAS)

# ---------------------------------------------------------
# COMUNICACIÓN CON LA RASPBERRY
# ---------------------------------------------------------

# Última respuesta recibida del jugador B (vía botón físico)
respuesta_jugador_b = ''
