import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk

def cargar_imagen():
    global imagen_original, imagen_actual, imagen_tk
    ruta_imagen = filedialog.askopenfilename(filetypes=[("Imágenes", "*.png;*.jpg;*.jpeg;*.bmp")])
    if ruta_imagen:
        imagen_original = Image.open(ruta_imagen)
        imagen_original.thumbnail((500, 500))  # Ajusta la imagen para caber en el canvas
        imagen_actual = imagen_original.copy()  # Copia para mantener la original sin modificaciones
        mostrar_imagen(imagen_actual)

def activar_recorte():
    global modo_recorte
    modo_recorte = True
    boton_recortar.config(text="Modo Recorte Activado", state="disabled")
    ventana.config(cursor="cross")  # Cambia el cursor a una cruz para indicar el modo de recorte

def iniciar_seleccion(event):
    global x_inicial, y_inicial, rectangulo
    if modo_recorte:
        x_inicial, y_inicial = event.x, event.y
        if rectangulo:
            etiqueta_imagen.delete(rectangulo)
        rectangulo = etiqueta_imagen.create_rectangle(x_inicial, y_inicial, x_inicial, y_inicial, outline='red', width=2)

def actualizar_seleccion(event):
    if modo_recorte:
        etiqueta_imagen.coords(rectangulo, x_inicial, y_inicial, event.x, event.y)

def terminar_seleccion(event):
    global x_inicial, y_inicial, imagen_actual, modo_recorte, rectangulo
    if modo_recorte:
        x_final, y_final = event.x, event.y
        if imagen_actual:
            x0, x1 = sorted([x_inicial, x_final])
            y0, y1 = sorted([y_inicial, y_final])
            # Recorta la imagen actual y actualiza la imagen actual con el recorte
            imagen_actual = imagen_actual.crop((x0, y0, x1, y1))
            mostrar_imagen(imagen_actual)
        
        # Desactiva el modo de recorte y limpia la interfaz
        modo_recorte = False
        boton_recortar.config(text="Recortar Imagen", state="normal")
        ventana.config(cursor="")  # Restablece el cursor al predeterminado
        etiqueta_imagen.delete(rectangulo)  # Elimina el rectángulo de selección

def mostrar_imagen(imagen):
    global imagen_tk
    imagen_tk = ImageTk.PhotoImage(imagen)
    etiqueta_imagen.create_image(0, 0, anchor="nw", image=imagen_tk)

def restaurar_imagen_original():
    global imagen_actual
    if imagen_original:
        imagen_actual = imagen_original.copy()  # Restaura la imagen actual a la original
        mostrar_imagen(imagen_actual)

# Configuración de la ventana
ventana = tk.Tk()
ventana.title("Cargar y Recortar Imagen Visualmente")
ventana.geometry("600x600")

# Variables globales
imagen_original = None
imagen_actual = None
x_inicial = y_inicial = 0
rectangulo = None
modo_recorte = False  # Estado para controlar el modo de recorte

# Botón para cargar la imagen
boton_cargar = tk.Button(ventana, text="Cargar Imagen", command=cargar_imagen)
boton_cargar.pack(pady=10)

# Botón para activar el modo de recorte
boton_recortar = tk.Button(ventana, text="Recortar Imagen", command=activar_recorte)
boton_recortar.pack(pady=10)

# Botón para restaurar la imagen original
boton_restaurar = tk.Button(ventana, text="Restaurar Imagen Original", command=restaurar_imagen_original)
boton_restaurar.pack(pady=10)

# Canvas para mostrar y dibujar sobre la imagen
etiqueta_imagen = tk.Canvas(ventana, width=500, height=500)
etiqueta_imagen.pack()
etiqueta_imagen.bind("<Button-1>", iniciar_seleccion)       # Al hacer clic, inicia la selección
etiqueta_imagen.bind("<B1-Motion>", actualizar_seleccion)   # Al arrastrar, actualiza el área seleccionada
etiqueta_imagen.bind("<ButtonRelease-1>", terminar_seleccion)  # Al soltar, termina la selección

ventana.mainloop()
