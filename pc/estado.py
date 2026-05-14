from constantes import FRASES_PREDETERMINADAS
 
 
# ---------------------------------------------------------
# CONEXIÓN
# ---------------------------------------------------------
 
ip_raspberry = ''
 
 
# ---------------------------------------------------------
# CONFIGURACIÓN DE PARTIDA
# ---------------------------------------------------------
 
modo_juego       = 1       # 1 = Transmisión Simple  /  2 = Escucha y Transmisión
nombre_jugador_a = 'JUGADOR A'
nombre_jugador_b = 'JUGADOR B'
lista_frases     = list(FRASES_PREDETERMINADAS)
 
 
# ---------------------------------------------------------
# ESTADO DE LA PARTIDA EN CURSO
# ---------------------------------------------------------
 
puntos_jugador_a = 0
puntos_jugador_b = 0
ronda_actual     = 0
frase_actual     = ''
 
# Velocidad de transmisión morse por ronda (ms por unidad)
# Ronda 1 = lenta, 2 = media, 3 = rápida
VELOCIDADES_POR_RONDA = {1: 300, 2: 200, 3: 120}
 
 
# ---------------------------------------------------------
# ESTADO DE LA RONDA — MODO 2
# ---------------------------------------------------------
 
# Fase dentro de la ronda:
#   'turno_1' -> A en PC, B en botón físico
#   'turno_2' -> A en botón físico, B en PC  (roles invertidos)
fase_modo2 = 'turno_1'
 
respuesta_morse_a_turno1 = ''
respuesta_morse_b_turno1 = ''
respuesta_morse_a_turno2 = ''
respuesta_morse_b_turno2 = ''
 
 
# ---------------------------------------------------------
# ENTRADA MORSE EN TIEMPO REAL (tecla K en la PC)
# ---------------------------------------------------------
 
codigo_morse_en_curso    = ''    # impulsos de la letra que se está pulsando ahora
texto_morse_acumulado    = ''    # letras ya decodificadas en esta sesión
tiempo_ultimo_evento_seg = 0.0   # marca de tiempo del último press/release
 
UMBRAL_RAYA_PC_SEG    = 0.3     # press < 0.3 s = punto  /  >= 0.3 s = raya
PAUSA_FIN_LETRA_SEG   = 0.6     # pausa sin actividad para cerrar una letra
PAUSA_FIN_PALABRA_SEG = 1.4     # pausa sin actividad para insertar espacio
 
 
# ---------------------------------------------------------
# CUENTA REGRESIVA
# ---------------------------------------------------------
 
SEGUNDOS_POR_RONDA = 30
segundos_restantes = SEGUNDOS_POR_RONDA
timer_activo       = False
id_timer_tkinter   = None       # ID del after() de Tkinter para cancelarlo
 
 
# ---------------------------------------------------------
# COMUNICACIÓN CON LA RASPBERRY
# ---------------------------------------------------------
 
# Última respuesta morse recibida del jugador que usa el botón físico.
# La actualiza red.py cuando llega un mensaje "MORSE_B|..."
respuesta_jugador_b = ''