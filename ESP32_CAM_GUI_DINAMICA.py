"""
===============================================================================
Proyecto: Espectrofotómetro Digital En Tiempo Real Para Uso Didáctico
Autores: 
Luis Octavio Pimienta Murillo
Alejandra Ochoa Gutiérrez
Correos: 
pimientaluis11@gmail.com
ochoaalejandra22@gmail.com
Descripción: 
Este programa implementa una interfaz gráfica utilizando Tkinter para la 
visualización y análisis en tiempo real del stream de video capturado por una 
ESP32-CAM. Incluye funcionalidades para mostrar el stream, calcular histogramas 
de color y perfiles de intensidad en tiempo real.

Librerías:
- OpenCV (cv2): Captura y procesamiento del video.
- Tkinter: Creación de la interfaz gráfica.
- Pillow (PIL): Conversión de frames para su uso en Tkinter.
- NumPy: Procesamiento eficiente de matrices de datos.
- Matplotlib: Visualización de gráficos en tiempo real.

Instrucciones:
1. Configura la dirección IP del ESP32-CAM en la variable `url`.
2. Asegúrate de que las librerías están instaladas.
3. Ajusta la configuración de la cámara y resolución según las instrucciones.
4. Ejecuta el programa y utiliza los botones de la interfaz para interactuar 
   con el stream y analizar los datos en tiempo real.
===============================================================================
"""

import cv2
from tkinter import Tk, Button, Label, Frame, Toplevel, ttk, messagebox
from PIL import Image, ImageTk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os
from datetime import datetime
import socket
from tkinter import Canvas

# Dirección del ESP32-CAM
url = "http://192.168.100.13:81/stream"

# Variables globales
cap = None
streaming = False
imagen_capturada = None
recorte_activo = None
resolucion_original = None
task_histograma = None
task_intensidad = None

# =============================================================================
# Funciones para verificar conexión
# =============================================================================

def check_connection(host, port, timeout=2):
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except Exception:
        return False

# =============================================================================
# Funciones de gestión del stream
# =============================================================================

def start_stream():
    global cap, streaming, resolucion_original
    if not streaming:
        try:
            host, port = url.split("//")[1].split(":")[0], int(url.split(":")[-1].split("/")[0])
            if not check_connection(host, port):
                raise ConnectionError("No hay conexión con el ESP32-CAM. Verifique el dispositivo y la red.")
            
            cap = cv2.VideoCapture(url)
            if not cap.isOpened():
                raise ConnectionError("No se pudo abrir el stream del ESP32-CAM. Intente nuevamente.")
            
            streaming = True
            boton_recorte.config(state="disabled", text="Detenga el Stream para Recortar")
            boton_resolucion.config(state="normal")
            boton_analisis.config(state="normal")
            update_frame()
            print("Stream iniciado.")
            
            if resolucion_original is None:
                _, frame = cap.read()
                if frame is not None:
                    resolucion_original = (frame.shape[1], frame.shape[0])

        except ConnectionError as ce:
            messagebox.showerror("Error de Conexión", str(ce))
            print(f"Error de conexión: {ce}")
        except Exception as e:
            messagebox.showerror("Error", f"Error inesperado: {e}")
            print(f"Error inesperado: {e}")

def stop_stream():
    global cap, streaming
    if streaming:
        streaming = False
        if cap is not None:
            cap.release()
        boton_recorte.config(state="normal", text="Recortar Stream")
        boton_analisis.config(state="disabled")
        print("Stream detenido.")

def update_frame():
    global cap, streaming, imagen_capturada, recorte_activo
    if streaming and cap is not None:
        ret, frame = cap.read()
        if ret:
            if recorte_activo:
                x0, y0, x1, y1 = recorte_activo
                frame = frame[y0:y1, x0:x1]
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)
            video_label.imgtk = imgtk
            video_label.configure(image=imgtk)
            imagen_capturada = img
        root.after(10, update_frame)

def reset_resolution():
    global recorte_activo
    recorte_activo = None
    print("Resolución original restaurada.")

# =============================================================================
# Funciones de recorte
# =============================================================================

def iniciar_recorte():
    if imagen_capturada:
        global rectangulo, x_inicial, y_inicial, recorte_activo

        original_width, original_height = imagen_capturada.width, imagen_capturada.height

        def iniciar_seleccion(event):
            global x_inicial, y_inicial, rectangulo
            x_inicial, y_inicial = event.x, event.y
            rectangulo = canvas.create_rectangle(x_inicial, y_inicial, x_inicial, y_inicial, outline="red", width=2)

        def actualizar_seleccion(event):
            canvas.coords(rectangulo, x_inicial, y_inicial, event.x, event.y)

        def finalizar_seleccion(event):
            global recorte_activo
            x_final, y_final = event.x, event.y
            canvas_width, canvas_height = canvas.winfo_width(), canvas.winfo_height()

            x0, x1 = sorted([x_inicial, x_final])
            y0, y1 = sorted([y_inicial, y_final])

            scaled_x0 = int(x0 * original_width / canvas_width)
            scaled_x1 = int(x1 * original_width / canvas_width)
            scaled_y0 = int(y0 * original_height / canvas_height)
            scaled_y1 = int(y1 * original_height / canvas_height)

            recorte_activo = (scaled_x0, scaled_y0, scaled_x1, scaled_y1)
            print(f"Área de recorte seleccionada (escalada): {recorte_activo}")
            ventana_recorte.destroy()

        ventana_recorte = Toplevel(root)
        ventana_recorte.title("Seleccionar Área de Recorte")
        ventana_recorte.geometry(f"{original_width}x{original_height}")

        canvas = Canvas(ventana_recorte, width=original_width, height=original_height)
        canvas.pack(fill="both", expand=True)
        imgtk = ImageTk.PhotoImage(image=imagen_capturada)
        canvas.image = imgtk
        canvas.create_image(0, 0, anchor="nw", image=imgtk)

        canvas.bind("<Button-1>", iniciar_seleccion)
        canvas.bind("<B1-Motion>", actualizar_seleccion)
        canvas.bind("<ButtonRelease-1>", finalizar_seleccion)

        rectangulo = None

# =============================================================================
# Funciones de análisis
# =============================================================================

def abrir_ventanas():
    if not streaming:
        print("El stream debe estar iniciado para acceder a esta funcionalidad.")
        return

    ventana_tabs = Toplevel(root)
    ventana_tabs.title("Análisis en Tiempo Real")
    ventana_tabs.geometry("800x600")
    tabs = ttk.Notebook(ventana_tabs)

    tab_histograma = ttk.Frame(tabs)
    tab_intensidad = ttk.Frame(tabs)
    tabs.add(tab_histograma, text="Histograma")
    tabs.add(tab_intensidad, text="Graficar Intensidad")
    tabs.pack(expand=1, fill="both")

    fig_histograma, ax_histograma = plt.subplots(figsize=(7, 5))
    fig_intensidad, ax_intensidad = plt.subplots(figsize=(7, 5))

    canvas_histograma = FigureCanvasTkAgg(fig_histograma, master=tab_histograma)
    canvas_histograma.get_tk_widget().pack(fill="both", expand=True)
    canvas_intensidad = FigureCanvasTkAgg(fig_intensidad, master=tab_intensidad)
    canvas_intensidad.get_tk_widget().pack(fill="both", expand=True)

    def actualizar_histograma():
        global task_histograma
        if streaming and imagen_capturada:
            ax_histograma.clear()
            rgb_array = np.array(imagen_capturada)
            r_values = np.mean(rgb_array[:, :, 0], axis=0)
            g_values = np.mean(rgb_array[:, :, 1], axis=0)
            b_values = np.mean(rgb_array[:, :, 2], axis=0)
            intensity_values = (r_values + g_values + b_values) / 3
            x = np.arange(rgb_array.shape[1])

            ax_histograma.plot(x, r_values, color='red', label='Rojo')
            ax_histograma.plot(x, g_values, color='green', label='Verde')
            ax_histograma.plot(x, b_values, color='blue', label='Azul')
            ax_histograma.plot(x, intensity_values, color='black', label='Intensidad')

            ax_histograma.set_title("Histograma Promedio")
            ax_histograma.set_xlabel("Posición X del Stream")
            ax_histograma.set_ylabel("Valor Promedio")
            ax_histograma.legend()
            ax_histograma.grid(True)

            canvas_histograma.draw()

        task_histograma = root.after(100, actualizar_histograma)

    def actualizar_intensidad():
        global task_intensidad
        if streaming and imagen_capturada:
            ax_intensidad.clear()
            gray_image = imagen_capturada.convert('L')
            gray_array = np.array(gray_image)
            intensity_profile = np.mean(gray_array, axis=0)
            x = np.arange(len(intensity_profile))

            ax_intensidad.plot(x, intensity_profile, color='black', label='Intensidad')

            ax_intensidad.set_title("Perfil de Intensidad")
            ax_intensidad.set_xlabel("Posición X del Stream")
            ax_intensidad.set_ylabel("Intensidad")
            ax_intensidad.legend()
            ax_intensidad.grid(True)

            canvas_intensidad.draw()

        task_intensidad = root.after(100, actualizar_intensidad)

    def on_close():
        global task_histograma, task_intensidad
        if task_histograma:
            root.after_cancel(task_histograma)
            task_histograma = None
        if task_intensidad:
            root.after_cancel(task_intensidad)
            task_intensidad = None
        ventana_tabs.destroy()

    ventana_tabs.protocol("WM_DELETE_WINDOW", on_close)
    actualizar_histograma()
    actualizar_intensidad()

# =============================================================================
# Cierre del programa
# =============================================================================

def cerrar_programa():
    global cap, task_histograma, task_intensidad
    if task_histograma:
        root.after_cancel(task_histograma)
    if task_intensidad:
        root.after_cancel(task_intensidad)
    if streaming:
        stop_stream()
    root.destroy()
    print("Programa cerrado correctamente.")

# =============================================================================
# Cargar portada
# =============================================================================

def cargar_portada():
    try:
        portada = Image.open("templates/portada_Fotónica.png")
        portada.thumbnail((300, 100))  # Ajusta el tamaño
        portada_tk = ImageTk.PhotoImage(portada)
        label_portada.config(image=portada_tk)
        label_portada.image = portada_tk
    except Exception as e:
        print(f"Error al cargar la portada: {e}")

# =============================================================================
# Interfaz gráfica principal
# =============================================================================

root = Tk()
root.title("Stream ESP32-CAM y Procesamiento de Imágenes")
root.geometry("1000x600")
root.protocol("WM_DELETE_WINDOW", cerrar_programa)

# Agregar la imagen de portada
label_portada = Label(root, bg="white")
label_portada.pack(pady=10)  # Espaciado para separar de los botones
cargar_portada()

frame_botones = Frame(root)
frame_botones.pack(side="left", padx=10, pady=10)

boton_iniciar = Button(frame_botones, text="Iniciar Stream", command=start_stream)
boton_iniciar.pack(pady=5)

boton_detener = Button(frame_botones, text="Detener Stream", command=stop_stream)
boton_detener.pack(pady=5)

boton_recorte = Button(frame_botones, text="Recortar Stream", command=iniciar_recorte, state="disabled")
boton_recorte.pack(pady=5)

boton_resolucion = Button(frame_botones, text="Resolución Original", command=reset_resolution, state="disabled")
boton_resolucion.pack(pady=5)

boton_analisis = Button(frame_botones, text="Análisis en Tiempo Real", command=abrir_ventanas, state="disabled")
boton_analisis.pack(pady=5)

video_label = Label(root, width=640, height=480, bg="black")
video_label.pack(side="right", padx=10, pady=10)

root.mainloop()
