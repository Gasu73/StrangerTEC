import tkinter as tk

from constantes import (
    COLOR_FONDO, COLOR_TEXTO, COLOR_ROJO,
    FUENTE_NORMAL, FUENTE_MEDIANA,
)


def limpiar_pantalla(contenedor, pantalla_actual):
    """
    Destruye el frame de la pantalla actual y devuelve uno nuevo.
    Se usa para hacer la transición entre pantallas.
    """
    if pantalla_actual:
        pantalla_actual.destroy()

    nueva_pantalla = tk.Frame(contenedor, bg=COLOR_FONDO)
    nueva_pantalla.pack(fill='both', expand=True)

    return nueva_pantalla


def crear_label(padre, texto='', fuente=FUENTE_NORMAL, color=COLOR_TEXTO, **kw):
    """Label con texto fijo."""
    return tk.Label(
        padre,
        text=texto,
        bg=COLOR_FONDO,
        fg=color,
        font=fuente,
        **kw
    )


def crear_label_variable(padre, variable, fuente=FUENTE_NORMAL, color=COLOR_TEXTO, **kw):
    """Label cuyo texto está ligado a una StringVar."""
    return tk.Label(
        padre,
        textvariable=variable,
        bg=COLOR_FONDO,
        fg=color,
        font=fuente,
        **kw
    )


def crear_boton(padre, texto, comando, ancho=20, color=COLOR_ROJO):
    """Botón con el estilo oscuro de la aplicación."""
    return tk.Button(
        padre,
        text=texto,
        command=comando,
        bg=color,
        fg=COLOR_TEXTO,
        font=FUENTE_NORMAL,
        relief='flat',
        width=ancho,
        cursor='hand2',
        pady=7,
        activebackground='#881111',
        activeforeground=COLOR_TEXTO,
    )


def crear_entrada(padre, variable, ancho=24):
    """Campo de texto con el estilo oscuro de la aplicación."""
    return tk.Entry(
        padre,
        textvariable=variable,
        bg='#222',
        fg=COLOR_TEXTO,
        insertbackground=COLOR_TEXTO,
        relief='flat',
        bd=4,
        font=FUENTE_MEDIANA,
        width=ancho,
    )


def crear_separador(padre):
    """Línea horizontal decorativa."""
    tk.Frame(padre, bg='#333', height=1).pack(fill='x', pady=10)
