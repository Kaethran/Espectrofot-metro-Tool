import cv2
from tkinter import Tk, Button, Label, Frame, filedialog, Canvas
from PIL import Image, ImageTk
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

# Dirección del ESP32-CAM
url = "http://192.168.100.13:81/stream"

# Variables globales
cap = None
streaming = False
imagen_capturada = None
imagen_original = None
imagen_actual = None
imagen_tk = None
rectangulo = None

# Funciones del stream
def start_stream():
    """Inicia o reanuda el stream."""
    global cap, streaming
    if not streaming:
        cap = cv2.VideoCapture(url)
        streaming = True
        boton_capturar.config(state="disabled")  # Deshabilitar el botón de capturar
        update_frame()
        print("Stream iniciado.")

def update_frame():
    """Actualiza el frame en la ventana de Tkinter."""
    global cap, streaming, imagen_capturada
    if streaming and cap is not None:
        ret, frame = cap.read()
        if ret:
            # Convertir el frame para Tkinter
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)

            # Guardar el último frame como referencia para captura
            imagen_capturada = img

            # Actualizar la imagen en el Label
            video_label.imgtk = imgtk
            video_label.configure(image=imgtk)

        # Reprogramar la función para el siguiente frame
        root.after(10, update_frame)

def stop_stream():
    """Detiene el stream."""
    global cap, streaming
    if streaming:
        streaming = False
        if cap is not None:
            cap.release()
        boton_capturar.config(state="normal")  # Habilitar el botón de capturar
        print("Stream detenido.")

# Función para capturar la imagen actual
def capturar_imagen():
    """Captura la imagen actual del stream."""
    global imagen_original, imagen_actual, imagen_capturada
    if imagen_capturada:
        imagen_original = imagen_capturada.copy()
        imagen_actual = imagen_original.copy()
        mostrar_imagen(imagen_actual)
        print("Imagen capturada.")

# Funciones de procesamiento de imágenes
def mostrar_imagen(imagen):
    """Muestra una imagen en el área de visualización."""
    global imagen_tk
    imagen_tk = ImageTk.PhotoImage(imagen)
    etiqueta_imagen.create_image(0, 0, anchor="nw", image=imagen_tk)

def cargar_imagen():
    """Carga una imagen desde el sistema de archivos."""
    global imagen_original, imagen_actual, imagen_tk
    ruta_imagen = filedialog.askopenfilename(filetypes=[("Imágenes", "*.png;*.jpg;*.jpeg;*.bmp")])
    if ruta_imagen:
        imagen_original = Image.open(ruta_imagen)
        imagen_original.thumbnail((500, 500))
        imagen_actual = imagen_original.copy()
        mostrar_imagen(imagen_actual)

def restaurar_imagen_original():
    """Restaura la imagen original cargada."""
    global imagen_actual
    if imagen_original:
        imagen_actual = imagen_original.copy()
        mostrar_imagen(imagen_actual)

def graficar_intensidad():
    """Grafica la intensidad promedio de la imagen."""
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
    """Muestra el histograma promedio de colores RGB e intensidad."""
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

# Ventana principal
root = Tk()
root.title("Stream ESP32-CAM y Procesamiento de Imágenes")
root.geometry("1000x600")

# Frame para organizar botones al lado del stream
frame_botones = Frame(root)
frame_botones.pack(side="left", padx=10, pady=10)

boton_iniciar = Button(frame_botones, text="Iniciar Stream", command=start_stream)
boton_iniciar.pack(pady=5)

boton_detener = Button(frame_botones, text="Detener Stream", command=stop_stream)
boton_detener.pack(pady=5)

boton_capturar = Button(frame_botones, text="Capturar Imagen", command=capturar_imagen, state="disabled")
boton_capturar.pack(pady=5)

boton_cargar = Button(frame_botones, text="Cargar Imagen", command=cargar_imagen)
boton_cargar.pack(pady=5)

boton_restaurar = Button(frame_botones, text="Restaurar Imagen Original", command=restaurar_imagen_original)
boton_restaurar.pack(pady=5)

boton_graficar = Button(frame_botones, text="Graficar Intensidad", command=graficar_intensidad)
boton_graficar.pack(pady=5)

boton_histograma = Button(frame_botones, text="Mostrar Histograma Promedio", command=mostrar_histograma_promedio)
boton_histograma.pack(pady=5)

# Sección del stream
video_label = Label(root, width=640, height=480, bg="black")
video_label.pack(side="right", padx=10, pady=10)

# Sección de procesamiento
etiqueta_imagen = Canvas(root, width=640, height=480)
etiqueta_imagen.pack(side="right", padx=10, pady=10)

# Ejecutar la interfaz gráfica
root.mainloop()
