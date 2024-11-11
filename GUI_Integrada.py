import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

def cargar_imagen():
    global imagen_original, imagen_actual, imagen_tk
    ruta_imagen = filedialog.askopenfilename(filetypes=[("Imágenes", "*.png;*.jpg;*.jpeg;*.bmp")])
    if ruta_imagen:
        imagen_original = Image.open(ruta_imagen)
        imagen_original.thumbnail((500, 500))
        imagen_actual = imagen_original.copy()
        mostrar_imagen(imagen_actual)

def activar_recorte():
    global modo_recorte
    modo_recorte = True
    boton_recortar.config(text="Modo Recorte Activado", state="disabled")
    ventana.config(cursor="cross")

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
            imagen_actual = imagen_actual.crop((x0, y0, x1, y1))
            mostrar_imagen(imagen_actual)
        
        modo_recorte = False
        boton_recortar.config(text="Recortar Imagen", state="normal")
        ventana.config(cursor="")
        etiqueta_imagen.delete(rectangulo)

def mostrar_imagen(imagen):
    global imagen_tk
    imagen_tk = ImageTk.PhotoImage(imagen)
    etiqueta_imagen.create_image(0, 0, anchor="nw", image=imagen_tk)

def restaurar_imagen_original():
    global imagen_actual
    if imagen_original:
        imagen_actual = imagen_original.copy()
        mostrar_imagen(imagen_actual)

def graficar_intensidad():
    if imagen_actual:
        gray_image = imagen_actual.convert('L')
        gray_array = np.array(gray_image)
        intensity_profile = np.mean(gray_array, axis=0)
        x = np.arange(len(intensity_profile))
        colors = ["#8B00FF", "#4B0082", "#0000FF", "#00FF00", "#FFFF00", "#FF7F00", "#FF0000"]
        cmap = mcolors.LinearSegmentedColormap.from_list("spectrum", colors)
        plt.figure(figsize=(10, 6))
        scatter = plt.scatter(x, intensity_profile, c=x, cmap=cmap, marker='o', edgecolor='none')
        plt.plot(intensity_profile, color='black', alpha=0.3)
        plt.title('Perfil de Intensidad del Espectro')
        plt.xlabel('Posición (longitud de onda aproximada)')
        plt.ylabel('Intensidad')
        plt.colorbar(scatter, orientation='horizontal', label='Color del espectro')
        plt.grid(True)
        plt.show()

ventana = tk.Tk()
ventana.title("Cargar y Recortar Imagen Visualmente")
ventana.geometry("600x600")

imagen_original = None
imagen_actual = None
x_inicial = y_inicial = 0
rectangulo = None
modo_recorte = False

boton_cargar = tk.Button(ventana, text="Cargar Imagen", command=cargar_imagen)
boton_cargar.pack(pady=10)

boton_recortar = tk.Button(ventana, text="Recortar Imagen", command=activar_recorte)
boton_recortar.pack(pady=10)

boton_restaurar = tk.Button(ventana, text="Restaurar Imagen Original", command=restaurar_imagen_original)
boton_restaurar.pack(pady=10)

boton_graficar = tk.Button(ventana, text="Graficar Intensidad", command=graficar_intensidad)
boton_graficar.pack(pady=10)

etiqueta_imagen = tk.Canvas(ventana, width=500, height=500)
etiqueta_imagen.pack()
etiqueta_imagen.bind("<Button-1>", iniciar_seleccion)
etiqueta_imagen.bind("<B1-Motion>", actualizar_seleccion)
etiqueta_imagen.bind("<ButtonRelease-1>", terminar_seleccion)

ventana.mainloop()
