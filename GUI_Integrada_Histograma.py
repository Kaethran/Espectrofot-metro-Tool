"""
===============================================================================
Proyecto: Espectrofotómetro Digital En De Imagen Para Uso Didáctico
Autores: 
Luis Octavio Pimienta Murillo
Alejandra Ochoa Gutiérrez
Correos: 
pimientaluis11@gmail.com
ochoaalejandra22@gmail.com
Descripción: 
Este programa implementa una interfaz gráfica para cargar, recortar y analizar 
imágenes utilizando Tkinter. Se incluye la funcionalidad para graficar el 
perfil de intensidad de un espectro y generar un histograma promedio de colores.

Librerías:
- Tkinter: Para la creación de la interfaz gráfica.
- Pillow (PIL): Para manipulación de imágenes y conversión a formatos compatibles.
- NumPy: Para realizar operaciones matemáticas en matrices de datos.
- Matplotlib: Para generar gráficos como histogramas y perfiles de intensidad.

Instrucciones:
1. Ejecute el programa y utilice los botones de la interfaz para cargar una 
   imagen desde su computadora.
2. Use la funcionalidad de recorte para seleccionar una región específica de 
   interés en la imagen cargada.
3. Genere gráficos como histogramas y perfiles de intensidad utilizando los 
   botones correspondientes.
4. La interfaz permite restaurar la imagen original en cualquier momento.

Nota: El programa está diseñado para trabajar con imágenes en formato PNG, JPG,
JPEG y BMP. Los gráficos se generan en ventanas emergentes.
===============================================================================
"""

import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import numpy as np
import matplotlib.pyplot as plt

# =============================================================================
# Funciones para manipulación de imágenes
# =============================================================================

def cargar_imagen():
    """
    Abre un cuadro de diálogo para seleccionar una imagen desde el sistema de 
    archivos. La imagen seleccionada se carga, se escala a un tamaño máximo 
    de 500x500 píxeles, y se muestra en la interfaz gráfica.
    """
    global imagen_original, imagen_actual, imagen_tk
    ruta_imagen = filedialog.askopenfilename(filetypes=[("Imágenes", "*.png;*.jpg;*.jpeg;*.bmp")])
    if ruta_imagen:
        imagen_original = Image.open(ruta_imagen)
        imagen_original.thumbnail((500, 500))
        imagen_actual = imagen_original.copy()
        mostrar_imagen(imagen_actual)

def activar_recorte():
    """
    Activa el modo de recorte, permitiendo al usuario dibujar un rectángulo 
    sobre la imagen cargada para seleccionar un área específica. 
    Cambia el texto del botón de recorte y ajusta el cursor de la interfaz.
    """
    global modo_recorte
    modo_recorte = True
    boton_recortar.config(text="Modo Recorte Activado", state="disabled")
    ventana.config(cursor="cross")

def iniciar_seleccion(event):
    """
    Captura las coordenadas iniciales del clic del usuario para comenzar la 
    selección del área de recorte.
    """
    global x_inicial, y_inicial, rectangulo
    if modo_recorte:
        x_inicial, y_inicial = event.x, event.y
        if rectangulo:
            etiqueta_imagen.delete(rectangulo)
        rectangulo = etiqueta_imagen.create_rectangle(x_inicial, y_inicial, x_inicial, y_inicial, outline='red', width=2)

def actualizar_seleccion(event):
    """
    Actualiza dinámicamente las dimensiones del rectángulo de selección mientras 
    el usuario arrastra el cursor.
    """
    global rectangulo
    if modo_recorte and rectangulo:
        etiqueta_imagen.coords(rectangulo, x_inicial, y_inicial, event.x, event.y)

def terminar_seleccion(event):
    """
    Finaliza el proceso de selección, recortando la imagen cargada según las 
    coordenadas seleccionadas por el usuario. Restaura el estado del cursor 
    y del botón de recorte.
    """
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
        if rectangulo:
            etiqueta_imagen.delete(rectangulo)
        rectangulo = None

def mostrar_imagen(imagen):
    """
    Muestra la imagen proporcionada en el área principal de la interfaz gráfica.
    """
    global imagen_tk
    imagen_tk = ImageTk.PhotoImage(imagen)
    etiqueta_imagen.create_image(0, 0, anchor="nw", image=imagen_tk)

def restaurar_imagen_original():
    """
    Restaura la imagen original cargada, reemplazando cualquier modificación o 
    recorte realizado previamente.
    """
    global imagen_actual
    if imagen_original:
        imagen_actual = imagen_original.copy()
        mostrar_imagen(imagen_actual)

# =============================================================================
# Funciones para análisis y graficación
# =============================================================================

def graficar_intensidad():
    """
    Genera un gráfico del perfil de intensidad en escala de grises de la 
    imagen cargada. Calcula el promedio de intensidad para cada columna de 
    píxeles.
    """
    if imagen_actual:
        gray_image = imagen_actual.convert('L')
        gray_array = np.array(gray_image)
        intensity_profile = np.mean(gray_array, axis=0)
        x = np.arange(len(intensity_profile))
        plt.figure(figsize=(10, 6))
        plt.plot(x, intensity_profile, color='black')
        plt.title('Perfil de Intensidad del Espectro')
        plt.xlabel('Eje X de la imagen')
        plt.ylabel('Intensidad')
        plt.grid(True)
        plt.show()

def mostrar_histograma():
    """
    Genera un histograma promedio de los canales de color (rojo, verde y azul)
    de la imagen cargada, mostrando las intensidades promedio en el eje X.
    """
    if imagen_actual:
        rgb_array = np.array(imagen_actual)
        r_values = np.mean(rgb_array[:, :, 0], axis=0)
        g_values = np.mean(rgb_array[:, :, 1], axis=0)
        b_values = np.mean(rgb_array[:, :, 2], axis=0)
        x = np.arange(rgb_array.shape[1])

        plt.figure(figsize=(10, 6))
        plt.plot(x, r_values, color='red', label='Rojo')
        plt.plot(x, g_values, color='green', label='Verde')
        plt.plot(x, b_values, color='blue', label='Azul')
        plt.title('Histograma Promedio de Colores (R, G, B)')
        plt.xlabel('Posición en X')
        plt.ylabel('Valor Promedio')
        plt.legend()
        plt.grid(True)
        plt.show()

# =============================================================================
# Configuración de la interfaz gráfica
# =============================================================================

ventana = tk.Tk()
ventana.title("Cargar y Recortar Imagen Visualmente")
ventana.geometry("800x700")
ventana.minsize(600, 700)

# Carga de imágenes de portada y logo
portada = Image.open("templates/portada_Fotónica.png")
portada.thumbnail((800, 100))
portada_tk = ImageTk.PhotoImage(portada)
label_portada = tk.Label(ventana, image=portada_tk)
label_portada.pack(pady=10)

frame_botones = tk.Frame(ventana)
frame_botones.place(relx=1.0, rely=0.25, anchor="ne")

# Botones de la interfaz
boton_cargar = tk.Button(frame_botones, text="Cargar Imagen", command=cargar_imagen)
boton_cargar.pack(pady=5)

boton_recortar = tk.Button(frame_botones, text="Recortar Imagen", command=activar_recorte)
boton_recortar.pack(pady=5)

boton_restaurar = tk.Button(frame_botones, text="Restaurar Imagen Original", command=restaurar_imagen_original)
boton_restaurar.pack(pady=5)

boton_graficar = tk.Button(frame_botones, text="Graficar Intensidad", command=graficar_intensidad)
boton_graficar.pack(pady=5)

boton_histograma = tk.Button(frame_botones, text="Mostrar Histograma", command=mostrar_histograma)
boton_histograma.pack(pady=5)

# Área para mostrar la imagen cargada
etiqueta_imagen = tk.Canvas(ventana, width=500, height=500)
etiqueta_imagen.pack(pady=(20, 0))

# Eventos para el recorte
etiqueta_imagen.bind("<Button-1>", iniciar_seleccion)
etiqueta_imagen.bind("<B1-Motion>", actualizar_seleccion)
etiqueta_imagen.bind("<ButtonRelease-1>", terminar_seleccion)

rectangulo = None  # Inicialización del rectángulo de selección

# Ejecutar la interfaz
ventana.mainloop()
