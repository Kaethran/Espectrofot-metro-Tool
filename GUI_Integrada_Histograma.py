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
    global rectangulo
    if modo_recorte and rectangulo:
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
        if rectangulo:
            etiqueta_imagen.delete(rectangulo)
        rectangulo = None  # Restablece rectangulo a None después del recorte

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

def mostrar_histograma_promedio():
    if imagen_actual:
        rgb_array = np.array(imagen_actual)
        r_values = np.mean(rgb_array[:, :, 0], axis=0)
        g_values = np.mean(rgb_array[:, :, 1], axis=0)
        b_values = np.mean(rgb_array[:, :, 2], axis=0)
        intensity_values = (r_values + g_values + b_values) / 3
        x = np.arange(rgb_array.shape[1])

        plt.figure(figsize=(10, 6))
        plt.plot(x, r_values, color='red', label='Rojo')
        plt.plot(x, g_values, color='green', label='Verde')
        plt.plot(x, b_values, color='blue', label='Azul')
        plt.plot(x, intensity_values, color='black', label='Intensidad', linestyle='--', alpha=0.7)
        plt.title('Histograma Promedio de Colores (R, G, B) e Intensidad en el Eje X')
        plt.xlabel('Posición en X')
        plt.ylabel('Valor Promedio')
        plt.legend()
        plt.grid(True)
        plt.show()

        width = rgb_array.shape[1]
        height = 100
        color_strip = np.zeros((height, width, 3), dtype=np.uint8)
        
        for i in range(width):
            color_strip[:, i, 0] = r_values[i]
            color_strip[:, i, 1] = g_values[i]
            color_strip[:, i, 2] = b_values[i]

        plt.figure(figsize=(10, 2))
        plt.imshow(color_strip)
        plt.axis('off')
        plt.title('Representación del Color Promedio a lo Largo del Eje X')
        plt.show()

# Función para colocar el logo en la esquina inferior derecha
def colocar_logo_udg():
    label_logo_udg.place(x=ventana.winfo_width() - 190, y=ventana.winfo_height() - 130)

ventana = tk.Tk()
ventana.title("Cargar y Recortar Imagen Visualmente")
ventana.geometry("800x700")
ventana.minsize(600, 700)

portada = Image.open("portada_Fotónica.png")
portada_width, portada_height = portada.size
new_height = 100
new_width = int((new_height / portada_height) * portada_width)
portada = portada.resize((new_width, new_height), Image.LANCZOS)
portada_tk = ImageTk.PhotoImage(portada)
label_portada = tk.Label(ventana, image=portada_tk)
label_portada.pack(pady=10)

frame_botones = tk.Frame(ventana)
frame_botones.place(relx=1.0, rely=0.25, anchor="ne")

boton_cargar = tk.Button(frame_botones, text="Cargar Imagen", command=cargar_imagen)
boton_cargar.pack(pady=5)

boton_recortar = tk.Button(frame_botones, text="Recortar Imagen", command=activar_recorte)
boton_recortar.pack(pady=5)

boton_restaurar = tk.Button(frame_botones, text="Restaurar Imagen Original", command=restaurar_imagen_original)
boton_restaurar.pack(pady=5)

boton_graficar = tk.Button(frame_botones, text="Graficar Intensidad", command=graficar_intensidad)
boton_graficar.pack(pady=5)

boton_histograma = tk.Button(frame_botones, text="Mostrar Histograma Promedio", command=mostrar_histograma_promedio)
boton_histograma.pack(pady=5)

etiqueta_imagen = tk.Canvas(ventana, width=500, height=500)
etiqueta_imagen.pack(pady=(20, 0))
etiqueta_imagen.bind("<Button-1>", iniciar_seleccion)
etiqueta_imagen.bind("<B1-Motion>", actualizar_seleccion)
etiqueta_imagen.bind("<ButtonRelease-1>", terminar_seleccion)

# Cargar y redimensionar el logo de la universidad a un tamaño más grande (180x120 píxeles) y aplicar transparencia
logo_udg = Image.open("udg_logo.png")
logo_udg = logo_udg.resize((180, 120), Image.LANCZOS)
logo_udg = logo_udg.convert("RGBA")  # Asegura que tiene canal alfa
alpha = 128  # Valor de transparencia (0 a 255, 128 es 50%)
logo_data = np.array(logo_udg)
logo_data[..., 3] = alpha  # Modifica el canal alfa para hacer transparente
logo_udg = Image.fromarray(logo_data)
logo_udg_tk = ImageTk.PhotoImage(logo_udg)
label_logo_udg = tk.Label(ventana, image=logo_udg_tk)

ventana.after(100, colocar_logo_udg)

rectangulo = None  # Inicialización global de rectangulo

ventana.mainloop()
