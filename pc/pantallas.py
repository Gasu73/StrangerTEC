# =========================================================
# pantallas.py
# Define las 4 pantallas de la aplicación.
# =========================================================
 
import tkinter as tk
from tkinter import messagebox
import random
import time
import threading
from PIL import Image, ImageTk
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
 
import estado
from constantes import (
    COLOR_FONDO, COLOR_TEXTO, COLOR_ROJO, COLOR_GRIS,
    COLOR_VERDE, COLOR_FONDO_OSCURO,
    FUENTE_TITULO, FUENTE_GRANDE, FUENTE_MEDIANA, FUENTE_NORMAL,
    MAXIMAS_RONDAS, MORSE_INVERSO,
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
 
 
ventana         = None
contenedor      = None
pantalla_actual = None
 
 
def inicializar(ventana_principal, contenedor_principal):
    global ventana, contenedor
    ventana    = ventana_principal
    contenedor = contenedor_principal
 
 
def _limpiar():
    global pantalla_actual
    _cancelar_timer()
    pantalla_actual = limpiar_pantalla(contenedor, pantalla_actual)
    return pantalla_actual
 
 
# =========================================================
# CUENTA REGRESIVA
# =========================================================
 
def _cancelar_timer():
    if estado.id_timer_tkinter is not None:
        try:
            ventana.after_cancel(estado.id_timer_tkinter)
        except Exception:
            pass
    estado.id_timer_tkinter = None
    estado.timer_activo     = False
 
 
def _iniciar_cuenta_regresiva(variable_timer, callback_fin):
    estado.segundos_restantes = estado.SEGUNDOS_POR_RONDA
    estado.timer_activo       = True
 
    def _tick():
        if not estado.timer_activo:
            return
 
        variable_timer.set(f'  {estado.segundos_restantes}s')
 
        if estado.segundos_restantes <= 0:
            estado.timer_activo = False
            variable_timer.set('  0s')
            callback_fin()
            return
 
        estado.segundos_restantes -= 1
        estado.id_timer_tkinter    = ventana.after(1000, _tick)
 
    _tick()
 
 
# =========================================================
# MORSE EN TIEMPO REAL — TECLA K
# =========================================================
 
# ID de los after() del cierre de letra y palabra
_id_cierre_letra   = None
_id_cierre_palabra = None
 
 
def _morse_key_press(evento, variable_impulso):
    """
    Se llama al presionar K.
    Ignora repeticiones automáticas del SO verificando que
    tiempo_ultimo_evento_seg esté en 0.
    """
    if estado.tiempo_ultimo_evento_seg != 0.0:
        return
    estado.tiempo_ultimo_evento_seg = time.time()
 
 
def _morse_key_release(evento, variable_impulso, variable_texto):
    """
    Se llama al soltar K.
    Calcula duración -> punto o raya y actualiza los displays.
    """
    global _id_cierre_letra, _id_cierre_palabra
 
    if estado.tiempo_ultimo_evento_seg == 0.0:
        return
 
    duracion = time.time() - estado.tiempo_ultimo_evento_seg
    estado.tiempo_ultimo_evento_seg = 0.0
 
    if duracion < estado.UMBRAL_RAYA_PC_SEG:
        estado.codigo_morse_en_curso += '.'
    else:
        estado.codigo_morse_en_curso += '-'
 
    variable_impulso.set(estado.codigo_morse_en_curso)
 
    # Cancelar temporizadores anteriores de cierre
    if _id_cierre_letra is not None:
        try:
            ventana.after_cancel(_id_cierre_letra)
        except Exception:
            pass
 
    if _id_cierre_palabra is not None:
        try:
            ventana.after_cancel(_id_cierre_palabra)
        except Exception:
            pass
 
    ms_letra   = int(estado.PAUSA_FIN_LETRA_SEG   * 1000)
    ms_palabra = int(estado.PAUSA_FIN_PALABRA_SEG  * 1000)
 
    def _cerrar_letra():
        global _id_cierre_palabra
        if estado.codigo_morse_en_curso == '':
            return
        letra = MORSE_INVERSO.get(estado.codigo_morse_en_curso, '?')
        estado.texto_morse_acumulado  += letra
        estado.codigo_morse_en_curso   = ''
        variable_impulso.set('')
        variable_texto.set(estado.texto_morse_acumulado)
 
        def _cerrar_palabra():
            if not estado.texto_morse_acumulado.endswith(' '):
                estado.texto_morse_acumulado += ' '
                variable_texto.set(estado.texto_morse_acumulado)
 
        _id_cierre_palabra = ventana.after(ms_palabra, _cerrar_palabra)
 
    _id_cierre_letra = ventana.after(ms_letra, _cerrar_letra)
 
 
def _resetear_morse_pc(variable_impulso=None, variable_texto=None):
    """Limpia todo el estado morse del jugador que usa la PC."""
    global _id_cierre_letra, _id_cierre_palabra
 
    estado.codigo_morse_en_curso    = ''
    estado.texto_morse_acumulado    = ''
    estado.tiempo_ultimo_evento_seg = 0.0
 
    for id_timer in [_id_cierre_letra, _id_cierre_palabra]:
        if id_timer is not None:
            try:
                ventana.after_cancel(id_timer)
            except Exception:
                pass
 
    _id_cierre_letra   = None
    _id_cierre_palabra = None
 
    if variable_impulso is not None:
        variable_impulso.set('')
 
    if variable_texto is not None:
        variable_texto.set('')
 
 
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
    crear_label_variable(
        pantalla, variable_estado_conexion, FUENTE_NORMAL, COLOR_ROJO
    ).pack(pady=6)
 
    def intentar_conexion():
        ip_ingresada = variable_ip.get().strip()
 
        if not ip_ingresada:
            variable_estado_conexion.set('Ingresa una IP primero')
            return
 
        variable_estado_conexion.set('Conectando...')
        ventana.update()
        estado.frase_actual = "Funda"
        conexion_exitosa = enviar_a_raspberry(ip_ingresada, 'ok', 200)
 
        if conexion_exitosa:
            estado.ip_raspberry = ip_ingresada
            variable_estado_conexion.set('Conectado!')
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
 
    crear_label(
        pantalla, 'CONFIGURAR PARTIDA', FUENTE_GRANDE, COLOR_ROJO
    ).pack(pady=(0, 14))
 
    formulario = tk.Frame(pantalla, bg=COLOR_FONDO)
    formulario.pack()
 
    crear_label(formulario, 'Jugador A:', FUENTE_NORMAL).grid(
        row=0, column=0, sticky='e', padx=14, pady=6)
    variable_nombre_a = tk.StringVar(value=estado.nombre_jugador_a)
    crear_entrada(formulario, variable_nombre_a, 18).grid(
        row=0, column=1, sticky='w', pady=6)
 
    crear_label(formulario, 'Jugador B:', FUENTE_NORMAL).grid(
        row=1, column=0, sticky='e', padx=14, pady=6)
    variable_nombre_b = tk.StringVar(value=estado.nombre_jugador_b)
    crear_entrada(formulario, variable_nombre_b, 18).grid(
        row=1, column=1, sticky='w', pady=6)
 
    crear_label(formulario, 'Modo de juego:', FUENTE_NORMAL).grid(
        row=2, column=0, sticky='ne', padx=14, pady=6)
 
    variable_modo = tk.IntVar(value=estado.modo_juego)
    marco_modos = tk.Frame(formulario, bg=COLOR_FONDO)
    marco_modos.grid(row=2, column=1, sticky='w', pady=6)
 
    for valor, descripcion in [
        (1, 'Transmision Simple'),
        (2, 'Escucha y Transmision'),
    ]:
        tk.Radiobutton(
            marco_modos,
            text=descripcion,
            variable=variable_modo,
            value=valor,
            bg=COLOR_FONDO, fg=COLOR_TEXTO,
            selectcolor='#333',
            activebackground=COLOR_FONDO,
            font=FUENTE_NORMAL,
        ).pack(anchor='w')
 
    crear_separador(pantalla)
 
    crear_label(
        pantalla, 'Frases del juego (max. 16 caracteres):', FUENTE_NORMAL
    ).pack()
 
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
                f'Maximo 16 caracteres (tiene {len(frase_nueva)}).',
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
        estado.frase_actual     = ''
        pantalla_juego()
 
    crear_boton(
        marco_botones, 'INICIAR PARTIDA', iniciar_partida, 18
    ).pack(side='left', padx=10)
 
    crear_boton(
        marco_botones, 'Volver', pantalla_conexion, 12, '#333333'
    ).pack(side='left', padx=10)
 
 
# =========================================================
# PANTALLA 3 — JUEGO
# =========================================================
 
def pantalla_juego():
 
    pantalla = _limpiar()
    
    try:
        pil_img = Image.open(os.path.join(BASE_DIR, 'morse.png')).resize((400, 230))  # ancho x alto en px
        img_morse = ImageTk.PhotoImage(pil_img)
        lbl_imagen = tk.Label(pantalla, image=img_morse, bg=COLOR_FONDO)
        lbl_imagen.image = img_morse
        lbl_imagen.pack(side='bottom', anchor='center', pady=(0, 0))
    except Exception:
        pass
    

    # --- Cabecera ---
    cab = tk.Frame(pantalla, bg=COLOR_FONDO_OSCURO)
    cab.pack(fill='x', pady=(0, 8))
    var_titulo = tk.StringVar()
    crear_label_variable(cab, var_titulo, FUENTE_GRANDE, COLOR_ROJO).pack(side='left', padx=14, pady=8)
    var_ronda = tk.StringVar()
    crear_label_variable(cab, var_ronda, FUENTE_NORMAL, COLOR_GRIS).pack(side='right', padx=14)
 
    # --- Morse de la frase + timer ---
    fila = tk.Frame(pantalla, bg=COLOR_FONDO)
    fila.pack(fill='x', padx=4)
    var_morse = tk.StringVar()
    crear_label_variable(fila, var_morse, FUENTE_NORMAL, COLOR_ROJO).pack(side='left')
    var_timer = tk.StringVar()
    crear_label_variable(fila, var_timer, FUENTE_GRANDE, COLOR_VERDE).pack(side='right', padx=14)
 
    # --- Instruccion ---
    var_instruccion = tk.StringVar()
    crear_label_variable(pantalla, var_instruccion, FUENTE_NORMAL, COLOR_GRIS).pack(anchor='w', padx=4, pady=4)
 
    crear_separador(pantalla)
 
    # --- Modo 1: campo de texto normal ---
    zona_m1 = tk.Frame(pantalla, bg=COLOR_FONDO)
    zona_m1.pack(fill='x', padx=4)
    var_nombre_a = tk.StringVar()
    crear_label_variable(zona_m1, var_nombre_a, FUENTE_NORMAL, COLOR_GRIS).pack(anchor='w')
    var_respuesta = tk.StringVar()
    campo_respuesta = crear_entrada(zona_m1, var_respuesta, 32)
    campo_respuesta.pack(anchor='w', pady=4)
    crear_label(zona_m1, 'Escribe la frase y presiona Enter', FUENTE_NORMAL, COLOR_GRIS).pack(anchor='w')
 
    # --- Modo 2: entrada morse con tecla K ---
    zona_m2 = tk.Frame(pantalla, bg=COLOR_FONDO)
    zona_m2.pack(fill='x', padx=4)
    var_nombre_pc = tk.StringVar()
    crear_label_variable(zona_m2, var_nombre_pc, FUENTE_NORMAL, COLOR_GRIS).pack(anchor='w')
    var_impulso = tk.StringVar()
    crear_label_variable(zona_m2, var_impulso, FUENTE_GRANDE, COLOR_ROJO).pack(anchor='w')
    var_texto_pc = tk.StringVar()
    crear_label_variable(zona_m2, var_texto_pc, FUENTE_GRANDE, COLOR_TEXTO).pack(anchor='w', pady=(0, 2))
    crear_label(zona_m2, 'Toca K = punto  |  mantén K = raya', FUENTE_NORMAL, COLOR_GRIS).pack(anchor='w')
 
    crear_separador(pantalla)
 
    # --- Modo 2: estado del jugador en el boton fisico ---
    var_nombre_boton = tk.StringVar()
    crear_label_variable(pantalla, var_nombre_boton, FUENTE_NORMAL, COLOR_GRIS).pack(anchor='w', padx=4)
    var_estado_boton = tk.StringVar()
    crear_label_variable(pantalla, var_estado_boton, FUENTE_NORMAL, COLOR_ROJO).pack(anchor='w', padx=4)
 
    crear_separador(pantalla)
 
    # --- Marcador ---
    marc = tk.Frame(pantalla, bg=COLOR_FONDO)
    marc.pack(fill='x')
    var_pts_a = tk.StringVar()
    var_pts_b = tk.StringVar()
    crear_label_variable(marc, var_pts_a, FUENTE_MEDIANA, COLOR_VERDE).pack(side='left', padx=14)
    crear_label_variable(marc, var_pts_b, FUENTE_MEDIANA, COLOR_VERDE).pack(side='right', padx=14)
 
    # ==========================================================
    # HELPERS
    # ==========================================================
 
    def actualizar_marcador():
        var_pts_a.set(f'{estado.nombre_jugador_a}: {estado.puntos_jugador_a} pts')
        var_pts_b.set(f'{estado.nombre_jugador_b}: {estado.puntos_jugador_b} pts')
 
    def mostrar_zona(modo1_visible):
        if modo1_visible:
            zona_m1.pack(fill='x', padx=4)
            zona_m2.pack_forget()
        else:
            zona_m1.pack_forget()
            zona_m2.pack(fill='x', padx=4)
 
    def activar_tecla_k():
        pantalla.focus_set()
        pantalla.bind('<KeyPress-k>',   lambda e: _morse_key_press(e, var_impulso))
        pantalla.bind('<KeyRelease-k>', lambda e: _morse_key_release(e, var_impulso, var_texto_pc))
 
    def desactivar_tecla_k():
        pantalla.unbind('<KeyPress-k>')
        pantalla.unbind('<KeyRelease-k>')
 
    def obtener_texto_pc():
        if estado.codigo_morse_en_curso:
            estado.texto_morse_acumulado += MORSE_INVERSO.get(estado.codigo_morse_en_curso, '?')
            estado.codigo_morse_en_curso  = ''
        return estado.texto_morse_acumulado.strip().upper()
 
    def evaluar(respuesta, jugador):
        correctas, total, pct = calcular_puntaje(estado.frase_actual, respuesta)
        pts = pct * estado.ronda_actual
        if jugador == 'A':
            estado.puntos_jugador_a += pts
            nombre = estado.nombre_jugador_a
        else:
            estado.puntos_jugador_b += pts
            nombre = estado.nombre_jugador_b
        actualizar_marcador()
        return f'{nombre}: "{respuesta}" -> {correctas}/{total} ({pct}%) +{pts}pts'
 
    def fin_partida():
        ganador = estado.nombre_jugador_a if estado.puntos_jugador_a >= estado.puntos_jugador_b else estado.nombre_jugador_b
        p_a = top10_agregar_entrada(estado.nombre_jugador_a, estado.puntos_jugador_a, f'Modo{estado.modo_juego}')
        p_b = top10_agregar_entrada(estado.nombre_jugador_b, estado.puntos_jugador_b, f'Modo{estado.modo_juego}')
        msg = f'GANADOR: {ganador}\n\n{estado.nombre_jugador_a}: {estado.puntos_jugador_a} pts'
        if p_a: msg += f'  (Top10 #{p_a})'
        msg += f'\n{estado.nombre_jugador_b}: {estado.puntos_jugador_b} pts'
        if p_b: msg += f'  (Top10 #{p_b})'
        messagebox.showinfo('Partida finalizada', msg, parent=ventana)
        pantalla_configuracion()
 
    def transmitir(velocidad):
        if estado.ip_raspberry:
            threading.Thread(
                target=enviar_a_raspberry,
                args=(estado.ip_raspberry, 'ok', velocidad),
                daemon=True,
            ).start()
 
    # ==========================================================
    # MODO 1 — el jugador escribe la frase en texto normal
    # ==========================================================
 
    def ronda_modo1():
        estado.ronda_actual += 1
        candidatas = [f for f in estado.lista_frases if f != estado.frase_actual] or estado.lista_frases
        estado.frase_actual = random.choice(candidatas).upper()
        velocidad = estado.VELOCIDADES_POR_RONDA.get(estado.ronda_actual, 200)
 
        var_ronda.set(f'Ronda {estado.ronda_actual}/{MAXIMAS_RONDAS}')
        var_titulo.set('Escucha y mira la maqueta')
        var_morse.set(texto_a_morse(estado.frase_actual))
        var_instruccion.set('Observa/escucha la maqueta y escribe la frase que recibiste.')
        var_nombre_a.set(estado.nombre_jugador_a)
        var_respuesta.set('')
        var_timer.set('')
        mostrar_zona(True)
        actualizar_marcador()
        transmitir(velocidad)
 
        campo_respuesta.bind('<Return>', lambda e: fin_modo1())
        campo_respuesta.focus_set()

 
    def fin_modo1():
        campo_respuesta.unbind('<Return>')
        resultado = evaluar(var_respuesta.get().strip().upper(), 'A')
        msg = f'Frase correcta: {estado.frase_actual}\n\n{resultado}'
        if estado.ronda_actual >= MAXIMAS_RONDAS:
            messagebox.showinfo('Resultado final', msg, parent=ventana)
            fin_partida()
        else:
            messagebox.showinfo(f'Ronda {estado.ronda_actual}', msg, parent=ventana)
            ronda_modo1()
 
    # ==========================================================
    # MODO 2 — A en PC (tecla K), B en boton fisico; luego se invierten
    # ==========================================================
 
    def ronda_modo2():
        estado.ronda_actual += 1
        candidatas = [f for f in estado.lista_frases if f != estado.frase_actual] or estado.lista_frases
        estado.frase_actual = random.choice(candidatas).upper()
        turno1_modo2()
 
    def turno1_modo2():
        # A: tecla K en PC  |  B: boton fisico (ACTIVAR_MORSE)
        estado.respuesta_jugador_b = ''
        velocidad = estado.VELOCIDADES_POR_RONDA.get(estado.ronda_actual, 200)
 
        var_ronda.set(f'Ronda {estado.ronda_actual}/{MAXIMAS_RONDAS}  — Turno 1/2')
        var_titulo.set('Escucha el morse — responde en codigo')
        var_morse.set(texto_a_morse(estado.frase_actual))
        var_instruccion.set('La Raspberry transmite la frase. Ambos responden en morse.')
        var_nombre_pc.set(f'{estado.nombre_jugador_a}  — tecla K')
        var_nombre_boton.set(f'{estado.nombre_jugador_b}  — boton fisico')
        var_estado_boton.set('Activando morse en la maqueta...')
 
        mostrar_zona(False)
        _resetear_morse_pc(var_impulso, var_texto_pc)
        actualizar_marcador()
        def transmitir_y_arrancar():
            # Bloquea hasta que la Raspberry termina de transmitir
            if estado.ip_raspberry:
                enviar_a_raspberry(estado.ip_raspberry, 'ok', velocidad)

            # Vuelta al hilo principal para activar la K y el timer
            ventana.after(0, _post_transmision_turno1)

        def _post_transmision_turno1():
            activar_tecla_k()
            var_estado_boton.set('Activando morse en la maqueta...')

            def activar_b():
                res = enviar_a_raspberry(estado.ip_raspberry, 'ACTIVAR_MORSE') if estado.ip_raspberry else ''
                estado.respuesta_jugador_b = res
                ventana.after(0, lambda: var_estado_boton.set(
                    f'{estado.nombre_jugador_b}: "{res or "(sin respuesta)"}"'))

            threading.Thread(target=activar_b, daemon=True).start()
            _iniciar_cuenta_regresiva(var_timer, fin_turno1_modo2)

        threading.Thread(target=transmitir_y_arrancar, daemon=True).start()
 
    def fin_turno1_modo2():
        desactivar_tecla_k()
        resp_a = obtener_texto_pc()
        resp_b = estado.respuesta_jugador_b.strip().upper()
        sin_resp = '(sin respuesta)'
        resumen = (
            f'{estado.nombre_jugador_a}: "{resp_a or sin_resp}"\n'
            f'{estado.nombre_jugador_b}: "{resp_b or sin_resp}"'
        )
        messagebox.showinfo('Turno 1 terminado', resumen, parent=ventana)
        # Guardar para evaluar al final del turno 2
        estado.respuesta_morse_a_turno1 = resp_a
        estado.respuesta_morse_b_turno1 = resp_b
        turno2_modo2()
 
    def turno2_modo2():
        # A: boton fisico (ACTIVAR_MORSE)  |  B: tecla K en PC
        estado.respuesta_jugador_b = ''
        velocidad = estado.VELOCIDADES_POR_RONDA.get(estado.ronda_actual, 200)
 
        var_ronda.set(f'Ronda {estado.ronda_actual}/{MAXIMAS_RONDAS}  — Turno 2/2 (roles invertidos)')
        var_titulo.set('Roles invertidos — misma frase')
        var_morse.set(texto_a_morse(estado.frase_actual))
        var_instruccion.set('Ahora los roles se invierten con la misma frase.')
        var_nombre_pc.set(f'{estado.nombre_jugador_b}  — tecla K')
        var_nombre_boton.set(f'{estado.nombre_jugador_a}  — boton fisico')
        var_estado_boton.set('Activando morse en la maqueta...')
 
        _resetear_morse_pc(var_impulso, var_texto_pc)
        actualizar_marcador()

        def transmitir_y_arrancar():
            if estado.ip_raspberry:
                enviar_a_raspberry(estado.ip_raspberry, 'ok', velocidad)
            ventana.after(0, _post_transmision_turno2)

        def _post_transmision_turno2():
            activar_tecla_k()
            var_estado_boton.set('Activando morse en la maqueta...')

            def activar_a():
                res = enviar_a_raspberry(estado.ip_raspberry, 'ACTIVAR_MORSE') if estado.ip_raspberry else ''
                estado.respuesta_jugador_b = res
                ventana.after(0, lambda: var_estado_boton.set(
                    f'{estado.nombre_jugador_a}: "{res or "(sin respuesta)"}"'))

            threading.Thread(target=activar_a, daemon=True).start()
            _iniciar_cuenta_regresiva(var_timer, fin_turno2_modo2)

        threading.Thread(target=transmitir_y_arrancar, daemon=True).start()
 
    def fin_turno2_modo2():
        desactivar_tecla_k()
        # En turno 2: B estaba en PC, A en el boton
        resp_b2 = obtener_texto_pc()
        resp_a2 = estado.respuesta_jugador_b.strip().upper()
 
        r_a1 = evaluar(estado.respuesta_morse_a_turno1, 'A')
        r_b1 = evaluar(estado.respuesta_morse_b_turno1, 'B')
        r_a2 = evaluar(resp_a2, 'A')
        r_b2 = evaluar(resp_b2, 'B')
 
        ganador = estado.nombre_jugador_a if estado.puntos_jugador_a > estado.puntos_jugador_b else (
                  estado.nombre_jugador_b if estado.puntos_jugador_b > estado.puntos_jugador_a else 'Empate')
 
        msg = (f'Frase: {estado.frase_actual}\n\n'
               f'Turno 1:\n{r_a1}\n{r_b1}\n\n'
               f'Turno 2:\n{r_a2}\n{r_b2}\n\n'
               f'Ganador de la ronda: {ganador}')
 
        if estado.ronda_actual >= MAXIMAS_RONDAS:
            messagebox.showinfo('Resultado final', msg, parent=ventana)
            fin_partida()
        else:
            messagebox.showinfo(f'Ronda {estado.ronda_actual}', msg, parent=ventana)
            ronda_modo2()
 
    # --- Arranque ---
    if estado.modo_juego == 1:
        ronda_modo1()
    else:
        ronda_modo2()
 
 
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
        crear_label(
            tabla, titulo, FUENTE_NORMAL, COLOR_ROJO, width=ancho, anchor='w'
        ).grid(row=0, column=columna, padx=6, pady=4)
 
    datos = top10_cargar()
 
    if not datos:
        crear_label(
            tabla, 'Todavia no hay puntajes guardados.', FUENTE_NORMAL, COLOR_GRIS
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
            'Confirmar', 'Borrar toda la tabla del Top 10?', parent=ventana
        )
        if confirmar:
            top10_guardar([])
            pantalla_top10(volver=volver)
 
    crear_boton(
        marco_botones, 'Volver', volver, 12, '#333333'
    ).pack(side='left', padx=10)
 
    crear_boton(
        marco_botones, 'Borrar tabla', borrar_top10, 14, '#331111'
    ).pack(side='left', padx=10)