import tkinter as tk
 
from constantes  import COLOR_FONDO
from pantallas   import inicializar, pantalla_conexion
 
 

# VENTANA PRINCIPAL
 
ventana = tk.Tk()
ventana.title('StrangerTEC — Morse Translator')
ventana.configure(bg=COLOR_FONDO)
ventana.resizable(False, False)
ventana.geometry('780x620')
 
contenedor_principal = tk.Frame(ventana, bg=COLOR_FONDO)
contenedor_principal.pack(fill='both', expand=True, padx=34, pady=22)
 

# INICIALIZAR MÓDULOS
 
# Pasar la ventana y el contenedor a pantallas.py
inicializar(ventana, contenedor_principal)
 




# ARRANQUE
 
pantalla_conexion()
ventana.mainloop()