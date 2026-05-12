# =========================================================
# pantallas.py
# Define las 4 pantallas de la aplicación:
#   1. Conexión
#   2. Configuración de partida
#   3. Juego
#   4. Top 10
# =========================================================

import tkinter as tk
from tkinter import messagebox
import random
import time
import threading

import estado
from constantes import (
    COLOR_FONDO, COLOR_TEXTO, COLOR_ROJO, COLOR_GRIS,
    COLOR_VERDE, COLOR_FONDO_OSCURO,
    FUENTE_TITULO, FUENTE_GRANDE, FUENTE_MEDIANA, FUENTE_NORMAL,
    MAXIMAS_RONDAS,
)
from widgets import (
    limpiar_pantalla, crear_label, crear_label_variable,
    crear_boton, crear_entrada, crear_separador,
)
from utilidades import (
    texto_a_morse, calcular_puntaje,
    top10_cargar, top10_guardar, top10_agregar_entrada,
)
from red import enviar_a_raspberry


# La ventana principal se recibe como parámetro para no
# crear dependencias circulares con main.py
ventana        = None
contenedor     = None
pantalla_actual = None


def inicializar(ventana_principal, contenedor_principal):
    """Debe llamarse desde main.py antes de mostrar cualquier pantalla."""
    global ventana, contenedor
    ventana    = ventana_principal
    contenedor = contenedor_principal


def _limpiar():
    """Wrapper interno que actualiza pantalla_actual."""
    global pantalla_actual
    pantalla_actual = limpiar_pantalla(contenedor, pantalla_actual)
    return pantalla_actual


# =========================================================
# PANTALLA 1 — CONEXIÓN
# =========================================================

def pantalla_conexion():

    pantalla = _limpiar()

    crear_label(pantalla, 'STRANGERTEC', FUENTE_TITULO, COLOR_ROJO).pack(pady=(10, 4))
    crear_label(pantalla, 'Morse Translator — ITCR', FUENTE_MEDIANA, COLOR_GRIS).pack()

    crear_separador(pantalla)

    crear_label(pantalla, 'IP de la Raspberry Pi:', FUENTE_NORMAL).pack(pady=(4, 4))

    variable_ip = tk.StringVar()
    crear_entrada(pantalla, variable_ip, 16).pack()

    variable_estado_conexion = tk.StringVar()
    crear_label_variable(pantalla, variable_estado_conexion, FUENTE_NORMAL, COLOR_ROJO).pack(pady=6)

    def intentar_conexion():
        ip_ingresada = variable_ip.get().strip()

        if not ip_ingresada:
            variable_estado_conexion.set('Ingresa una IP primero')
            return

        variable_estado_conexion.set('Conectando...')
        ventana.update()

        conexion_exitosa = enviar_a_raspberry(ip_ingresada, 'ambos', 'HOLA', 200)

        if conexion_exitosa:
            estado.ip_raspberry = ip_ingresada
            variable_estado_conexion.set('¡Conectado!')
        else:
            variable_estado_conexion.set('Error — verifica la IP')

    crear_boton(pantalla, 'CONECTAR', intentar_conexion, 22).pack(pady=10)

    crear_boton(
        pantalla, 'INICIAR JUEGO', pantalla_configuracion, 28, '#333333'
    ).pack(pady=2)

    crear_separador(pantalla)

    crear_boton(
        pantalla, 'Ver Top 10',
        lambda: pantalla_top10(volver=pantalla_conexion),
        18, '#333333'
    ).pack()


# =========================================================
# PANTALLA 2 — CONFIGURACIÓN DE PARTIDA
# =========================================================

def pantalla_configuracion():

    pantalla = _limpiar()

    crear_label(pantalla, 'CONFIGURAR PARTIDA', FUENTE_GRANDE, COLOR_ROJO).pack(pady=(0, 14))

    formulario = tk.Frame(pantalla, bg=COLOR_FONDO)
    formulario.pack()

    # --- Nombres ---
    crear_label(formulario, 'Jugador A (teclado):', FUENTE_NORMAL).grid(
        row=0, column=0, sticky='e', padx=14, pady=6)
    variable_nombre_a = tk.StringVar(value=estado.nombre_jugador_a)
    crear_entrada(formulario, variable_nombre_a, 18).grid(row=0, column=1, sticky='w', pady=6)

    crear_label(formulario, 'Jugador B (botón físico):', FUENTE_NORMAL).grid(
        row=1, column=0, sticky='e', padx=14, pady=6)
    variable_nombre_b = tk.StringVar(value=estado.nombre_jugador_b)
    crear_entrada(formulario, variable_nombre_b, 18).grid(row=1, column=1, sticky='w', pady=6)

    # --- Modo de juego ---
    crear_label(formulario, 'Modo de juego:', FUENTE_NORMAL).grid(
        row=2, column=0, sticky='ne', padx=14, pady=6)

    variable_modo = tk.IntVar(value=estado.modo_juego)
    marco_modos = tk.Frame(formulario, bg=COLOR_FONDO)
    marco_modos.grid(row=2, column=1, sticky='w', pady=6)

    for valor, descripcion in [(1, 'Transmisión Simple'), (2, 'Escucha y Transmisión')]:
        tk.Radiobutton(
            marco_modos,
            text=descripcion,
            variable=variable_modo,
            value=valor,
            bg=COLOR_FONDO,
            fg=COLOR_TEXTO,
            selectcolor='#333',
            activebackground=COLOR_FONDO,
            font=FUENTE_NORMAL,
        ).pack(anchor='w')

    crear_separador(pantalla)

    # --- Lista de frases ---
    crear_label(pantalla, 'Frases del juego (máx. 16 caracteres):', FUENTE_NORMAL).pack()

    marco_lista = tk.Frame(pantalla, bg=COLOR_FONDO)
    marco_lista.pack(pady=6)

    barra_scroll = tk.Scrollbar(marco_lista)
    barra_scroll.pack(side='right', fill='y')

    lista_widget = tk.Listbox(
        marco_lista,
        yscrollcommand=barra_scroll.set,
        bg='#222', fg=COLOR_TEXTO,
        font=FUENTE_NORMAL,
        selectbackground='#441111',
        height=4, width=22,
        relief='flat',
    )
    lista_widget.pack(side='left')
    barra_scroll.config(command=lista_widget.yview)

    for frase in estado.lista_frases:
        lista_widget.insert(tk.END, frase)

    marco_frases = tk.Frame(pantalla, bg=COLOR_FONDO)
    marco_frases.pack(pady=4)

    variable_frase_nueva = tk.StringVar()
    crear_entrada(marco_frases, variable_frase_nueva, 14).pack(side='left', padx=6)

    def agregar_frase():
        frase_nueva = variable_frase_nueva.get().upper().strip()

        if not frase_nueva:
            return

        if len(frase_nueva) > 16:
            messagebox.showwarning(
                'Demasiado larga',
                f'Máximo 16 caracteres (tiene {len(frase_nueva)}).',
                parent=ventana,
            )
            return

        if frase_nueva not in estado.lista_frases:
            estado.lista_frases.append(frase_nueva)
            lista_widget.insert(tk.END, frase_nueva)

        variable_frase_nueva.set('')

    def quitar_frase():
        seleccion = lista_widget.curselection()

        if seleccion:
            frase_a_quitar = lista_widget.get(seleccion[0])
            estado.lista_frases.remove(frase_a_quitar)
            lista_widget.delete(seleccion[0])

    crear_boton(marco_frases, '+ Agregar', agregar_frase, 10).pack(side='left', padx=4)
    crear_boton(marco_frases, '- Quitar',  quitar_frase,  8, '#333333').pack(side='left')

    crear_separador(pantalla)

    marco_botones = tk.Frame(pantalla, bg=COLOR_FONDO)
    marco_botones.pack()

    def iniciar_partida():
        estado.nombre_jugador_a = variable_nombre_a.get().strip() or 'JUGADOR A'
        estado.nombre_jugador_b = variable_nombre_b.get().strip() or 'JUGADOR B'
        estado.modo_juego       = variable_modo.get()
        estado.puntos_jugador_a = 0
        estado.puntos_jugador_b = 0
        estado.ronda_actual     = 0

        pantalla_juego()

    crear_boton(marco_botones, 'INICIAR PARTIDA', iniciar_partida, 18).pack(side='left', padx=10)
    crear_boton(marco_botones, 'Volver', pantalla_conexion, 12, '#333333').pack(side='left', padx=10)


# =========================================================
# PANTALLA 3 — JUEGO
# =========================================================

def pantalla_juego():

    pantalla = _limpiar()

    # --- Cabecera ---
    cabecera = tk.Frame(pantalla, bg=COLOR_FONDO_OSCURO)
    cabecera.pack(fill='x', pady=(0, 10))

    variable_titulo = tk.StringVar(value='TRANSMITIENDO')
    crear_label_variable(
        cabecera, variable_titulo, FUENTE_GRANDE, COLOR_ROJO
    ).pack(side='left', padx=14, pady=8)

    variable_ronda = tk.StringVar()
    crear_label_variable(
        cabecera, variable_ronda, FUENTE_NORMAL, COLOR_GRIS
    ).pack(side='right', padx=14)

    # --- Código Morse ---
    crear_label(pantalla, 'Código Morse de la frase:', FUENTE_NORMAL, COLOR_GRIS).pack(anchor='w')
    variable_codigo_morse = tk.StringVar()
    crear_label_variable(
        pantalla, variable_codigo_morse, FUENTE_GRANDE, COLOR_ROJO
    ).pack(anchor='w', pady=4)

    # --- Frase revelada al evaluar ---
    variable_frase_revelada = tk.StringVar()
    crear_label_variable(
        pantalla, variable_frase_revelada, FUENTE_GRANDE, COLOR_TEXTO
    ).pack(anchor='w', pady=2)

    crear_separador(pantalla)

    # --- Instrucción e input jugador A ---
    variable_instruccion = tk.StringVar()
    crear_label_variable(
        pantalla, variable_instruccion, FUENTE_NORMAL, COLOR_GRIS
    ).pack(anchor='w')

    marco_input = tk.Frame(pantalla, bg=COLOR_FONDO)
    marco_input.pack(anchor='w', pady=8)

    variable_respuesta_a = tk.StringVar()
    campo_respuesta = crear_entrada(marco_input, variable_respuesta_a, 22)
    campo_respuesta.pack(side='left', padx=(0, 12))

    def al_confirmar_jugador_a(evento=None):

        texto_ingresado = variable_respuesta_a.get().strip()

        if not texto_ingresado:
            messagebox.showwarning('Campo vacío', 'Escribe algo primero.', parent=ventana)
            return

        if estado.modo_juego == 1:
            # Modo simple: solo compite el jugador A
            evaluar_ronda(texto_ingresado, '')

        elif estado.turno_actual == 'A':
            # Guardar respuesta A y esperar la de B
            estado.respuesta_guardada_a = texto_ingresado
            estado.turno_actual         = 'B'

            variable_titulo.set(f'TURNO DE {estado.nombre_jugador_b} — botón físico')
            variable_instruccion.set(
                f'Esperando que {estado.nombre_jugador_b} ingrese su respuesta con el botón...'
            )
            variable_estado_b.set(f'{estado.nombre_jugador_b} usa el botón de la maqueta')

            boton_confirmar.config(state='disabled')
            campo_respuesta.config(state='disabled')

            # Escuchar en segundo plano la respuesta de la Raspberry
            hilo_espera = threading.Thread(
                target=_esperar_respuesta_jugador_b,
                daemon=True,
            )
            hilo_espera.start()

    campo_respuesta.bind('<Return>', al_confirmar_jugador_a)

    boton_confirmar = crear_boton(marco_input, 'CONFIRMAR', al_confirmar_jugador_a, 14)
    boton_confirmar.pack(side='left')

    # --- Estado del jugador B ---
    variable_estado_b = tk.StringVar()
    crear_label_variable(
        pantalla, variable_estado_b, FUENTE_NORMAL, COLOR_ROJO
    ).pack(anchor='w', pady=4)

    crear_separador(pantalla)

    # --- Marcador ---
    marco_puntajes = tk.Frame(pantalla, bg=COLOR_FONDO)
    marco_puntajes.pack(fill='x')

    variable_puntos_a = tk.StringVar()
    variable_puntos_b = tk.StringVar()

    crear_label_variable(
        marco_puntajes, variable_puntos_a, FUENTE_MEDIANA, COLOR_VERDE
    ).pack(side='left', padx=14)

    crear_label_variable(
        marco_puntajes, variable_puntos_b, FUENTE_MEDIANA, COLOR_VERDE
    ).pack(side='right', padx=14)

    # ----------------------------------------------------------
    # Funciones internas de la pantalla de juego
    # ----------------------------------------------------------

    def actualizar_marcador():
        variable_puntos_a.set(f'{estado.nombre_jugador_a}: {estado.puntos_jugador_a} pts')
        variable_puntos_b.set(f'{estado.nombre_jugador_b}: {estado.puntos_jugador_b} pts')

    def nueva_ronda():
        estado.ronda_actual += 1

        # Elegir frase sin repetir la anterior
        candidatas = [f for f in estado.lista_frases if f != estado.frase_actual]

        if not candidatas:
            candidatas = estado.lista_frases

        estado.frase_actual          = random.choice(candidatas).upper()
        estado.turno_actual          = 'A'
        estado.respuesta_guardada_a  = ''

        variable_ronda.set(f'Ronda {estado.ronda_actual}/{MAXIMAS_RONDAS}')
        variable_titulo.set('TRANSMITIENDO')
        variable_codigo_morse.set(texto_a_morse(estado.frase_actual))
        variable_frase_revelada.set('')
        variable_respuesta_a.set('')
        variable_estado_b.set('')
        variable_instruccion.set(
            f'{estado.nombre_jugador_a} — escribe la frase que descifraste:'
        )

        boton_confirmar.config(state='normal')
        campo_respuesta.config(state='normal')

        actualizar_marcador()
        campo_respuesta.focus()

        # Enviar la frase a la Raspberry para que la transmita
        if estado.ip_raspberry:
            enviar_a_raspberry(estado.ip_raspberry, 'ambos', estado.frase_actual, 200)

    def evaluar_ronda(respuesta_a, respuesta_b):

        correctas_a, total_letras, porcentaje_a = calcular_puntaje(estado.frase_actual, respuesta_a)
        ganadas_a = porcentaje_a * estado.nivel_juego
        estado.puntos_jugador_a += ganadas_a

        variable_frase_revelada.set(f'Frase correcta: {estado.frase_actual}')

        mensaje_resultado = (
            f'Frase correcta: {estado.frase_actual}\n\n'
            f'{estado.nombre_jugador_a}: {correctas_a}/{total_letras} '
            f'correctas ({porcentaje_a}%)  →  +{ganadas_a} pts'
        )

        if respuesta_b:
            correctas_b, _, porcentaje_b = calcular_puntaje(estado.frase_actual, respuesta_b)
            ganadas_b = porcentaje_b * estado.nivel_juego
            estado.puntos_jugador_b += ganadas_b
            mensaje_resultado += (
                f'\n{estado.nombre_jugador_b}: {correctas_b}/{total_letras} '
                f'correctas ({porcentaje_b}%)  →  +{ganadas_b} pts'
            )

        actualizar_marcador()

        if estado.ronda_actual >= MAXIMAS_RONDAS:
            messagebox.showinfo('Resultado final', mensaje_resultado, parent=ventana)
            terminar_partida()
        else:
            messagebox.showinfo(f'Ronda {estado.ronda_actual}', mensaje_resultado, parent=ventana)
            nueva_ronda()

    def _esperar_respuesta_jugador_b():
        """
        Hilo de espera: hace polling cada 500 ms sobre
        estado.respuesta_jugador_b (que actualiza red.py).
        Tiempo máximo de espera: 120 segundos.
        """
        estado.respuesta_jugador_b = ''   # limpiar antes de esperar

        tiempo_limite  = 120
        intervalo      = 0.5
        tiempo_pasado  = 0

        while tiempo_pasado < tiempo_limite:
            if estado.respuesta_jugador_b != '':
                respuesta_capturada = estado.respuesta_jugador_b
                # Volver al hilo principal de Tkinter para actualizar la UI
                ventana.after(0, lambda r=respuesta_capturada: _procesar_respuesta_b(r))
                return
            time.sleep(intervalo)
            tiempo_pasado += intervalo

        # Tiempo agotado
        ventana.after(
            0,
            lambda: variable_estado_b.set('Tiempo agotado — sin respuesta del botón')
        )

    def _procesar_respuesta_b(respuesta):
        """Se ejecuta en el hilo principal al recibir la respuesta de B."""
        variable_estado_b.set(f'{estado.nombre_jugador_b} respondió: {respuesta}')
        evaluar_ronda(estado.respuesta_guardada_a, respuesta)

    def terminar_partida():

        if estado.puntos_jugador_a >= estado.puntos_jugador_b:
            ganador = estado.nombre_jugador_a
        else:
            ganador = estado.nombre_jugador_b

        posicion_a = top10_agregar_entrada(
            estado.nombre_jugador_a, estado.puntos_jugador_a, f'Modo{estado.modo_juego}'
        )
        posicion_b = top10_agregar_entrada(
            estado.nombre_jugador_b, estado.puntos_jugador_b, f'Modo{estado.modo_juego}'
        )

        mensaje_final = (
            f'GANADOR: {ganador}\n\n'
            f'{estado.nombre_jugador_a}: {estado.puntos_jugador_a} pts'
        )

        if posicion_a:
            mensaje_final += f'  (Top 10 #{posicion_a})'

        mensaje_final += f'\n{estado.nombre_jugador_b}: {estado.puntos_jugador_b} pts'

        if posicion_b:
            mensaje_final += f'  (Top 10 #{posicion_b})'

        messagebox.showinfo('Partida finalizada', mensaje_final, parent=ventana)
        pantalla_configuracion()

    # Arrancar la primera ronda
    nueva_ronda()


# =========================================================
# PANTALLA 4 — TOP 10
# =========================================================

def pantalla_top10(volver=None):

    if volver is None:
        volver = pantalla_configuracion

    pantalla = _limpiar()

    crear_label(pantalla, 'TOP 10', FUENTE_TITULO, COLOR_ROJO).pack(pady=(0, 14))

    tabla = tk.Frame(pantalla, bg=COLOR_FONDO)
    tabla.pack()

    encabezados = ['#',  'Nombre', 'Puntos', 'Modo', 'Fecha']
    anchos      = [3,    14,       8,         10,     10     ]

    for columna, (titulo, ancho) in enumerate(zip(encabezados, anchos)):
        crear_label(tabla, titulo, FUENTE_NORMAL, COLOR_ROJO, width=ancho, anchor='w').grid(
            row=0, column=columna, padx=6, pady=4)

    datos = top10_cargar()

    if not datos:
        crear_label(
            tabla, 'Todavía no hay puntajes guardados.', FUENTE_NORMAL, COLOR_GRIS
        ).grid(row=1, column=0, columnspan=5, pady=20)

    else:
        for posicion, entrada in enumerate(datos, 1):

            if posicion <= 3:
                color_fila = COLOR_ROJO
            else:
                color_fila = COLOR_TEXTO

            valores = [
                str(posicion),
                entrada.get('nombre', ''),
                str(entrada.get('puntos', 0)),
                entrada.get('modo',   ''),
                entrada.get('fecha',  ''),
            ]

            for columna, (valor, ancho) in enumerate(zip(valores, anchos)):
                crear_label(
                    tabla, valor, FUENTE_NORMAL, color_fila, width=ancho, anchor='w'
                ).grid(row=posicion, column=columna, padx=6, pady=2)

    crear_separador(pantalla)

    marco_botones = tk.Frame(pantalla, bg=COLOR_FONDO)
    marco_botones.pack()

    def borrar_top10():
        confirmar = messagebox.askyesno(
            'Confirmar', '¿Borrar toda la tabla del Top 10?', parent=ventana
        )
        if confirmar:
            top10_guardar([])
            pantalla_top10(volver=volver)

    crear_boton(marco_botones, 'Volver', volver, 12, '#333333').pack(side='left', padx=10)
    crear_boton(marco_botones, 'Borrar tabla', borrar_top10, 14, '#331111').pack(side='left', padx=10)
