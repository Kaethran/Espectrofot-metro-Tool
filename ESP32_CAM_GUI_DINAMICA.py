"""
===============================================================================
Proyecto: Espectrofotómetro Digital Para Uso Didáctico
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
1. Configura la dirección IP del ESP32-CAM en la variable `url` (se debería de ver en el monitor serial tras cargar el código en Arduino y reiniciar el ESP32-CAM).
2. Asegúrate de que las librerías están instaladas.
3. Ingresa a la dirección IP proporcionada por el ESP32-CAM en Arduino:
   - Quita el filtro "Auto" en la sección "WB Mode", seleccionando una opción como "Home" u "Office" (fueron las que mejores resultados nos dieron).
   - Ajusta la resolución del stream según sea necesario para visualizar correctamente el stream en la GUI. 
4. Ejecuta el programa y utiliza los botones de la interfaz para interactuar 
   con el stream y analizar los datos en tiempo real.

Nota: Dependiendo de la resolución seleccionada y las características del monitor, 
la interfaz gráfica puede variar ligeramente en su presentación. Esto afecta 
principalmente las siguientes funciones del código:
   - `update_frame()`: Captura y ajusta los frames del stream. La calidad y el tamaño del frame dependerán de la resolución configurada en la IP del ESP32-CAM.
   - `Label` en la función principal: El área donde se muestra el video está configurada con un tamaño fijo (640x480 píxeles) en la GUI. Esto puede ser modificado para adaptarse a resoluciones más altas o bajas.
===============================================================================
"""

import cv2
from tkinter import Tk, Button, Label, Frame, Canvas, Toplevel, ttk
from PIL import Image, ImageTk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.colors as mcolors
import os
from datetime import datetime  # Para generar nombres únicos de capturas

# Dirección del ESP32-CAM
url = "http://192.168.100.13:81/stream"

# Variables globales
cap = None  # Objeto para capturar el stream
streaming = False  # Estado del stream
imagen_capturada = None  # Último frame capturado
task_intensidad = None  # Tarea de actualización del gráfico de intensidad
task_histograma = None  # Tarea de actualización del histograma

# =============================================================================
# Funciones para la gestión del stream
# =============================================================================

def start_stream():
    """
    Inicia o reanuda el stream desde el ESP32-CAM.
    Activa el botón para el análisis en tiempo real.
    """
    global cap, streaming
    if not streaming:
        cap = cv2.VideoCapture(url)
        streaming = True
        boton_analisis.config(state="normal")  # Habilitar el análisis
        update_frame()
        print("Stream iniciado.")

def update_frame():
    """
    Actualiza el frame capturado desde el ESP32-CAM en la ventana de Tkinter.
    Convierte el frame de formato BGR a RGB para su visualización.
    """
    global cap, streaming, imagen_capturada
    if streaming and cap is not None:
        ret, frame = cap.read()
        if ret:
            # Conversión de BGR a RGB
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)

            # Guardar el último frame capturado
            imagen_capturada = img

            # Actualizar el frame en el Label de video
            video_label.imgtk = imgtk
            video_label.configure(image=imgtk)

        # Llamar a esta función nuevamente después de 10 ms
        root.after(10, update_frame)

def stop_stream():
    """
    Detiene el stream desde el ESP32-CAM.
    Libera los recursos asociados con la captura de video.
    """
    global cap, streaming
    if streaming:
        streaming = False
        if cap is not None:
            cap.release()
        boton_analisis.config(state="disabled")  # Deshabilitar análisis
        print("Stream detenido.")

# =============================================================================
# Funciones para el análisis de imágenes
# =============================================================================

def abrir_ventanas():
    """
    Abre una ventana con dos pestañas para mostrar el histograma y el gráfico 
    de intensidad en tiempo real.
    Incluye la funcionalidad para guardar las gráficas como imágenes en una 
    carpeta llamada 'Capturas'.
    """
    if not streaming:
        print("El stream debe estar iniciado para acceder a esta funcionalidad.")
        return

    # Crear ventana con pestañas
    ventana_tabs = Toplevel(root)
    ventana_tabs.title("Análisis en Tiempo Real")
    ventana_tabs.geometry("800x600")
    tabs = ttk.Notebook(ventana_tabs)

    # Pestañas
    tab_histograma = ttk.Frame(tabs)
    tab_intensidad = ttk.Frame(tabs)
    tabs.add(tab_histograma, text="Histograma")
    tabs.add(tab_intensidad, text="Graficar Intensidad")
    tabs.pack(expand=1, fill="both")

    # Crear gráficos con Matplotlib
    fig_histograma, ax_histograma = plt.subplots(figsize=(7, 5))
    fig_intensidad, ax_intensidad = plt.subplots(figsize=(7, 5))

    # Canvas para incrustar gráficos
    canvas_histograma = FigureCanvasTkAgg(fig_histograma, master=tab_histograma)
    canvas_histograma.get_tk_widget().pack(fill="both", expand=True)
    canvas_intensidad = FigureCanvasTkAgg(fig_intensidad, master=tab_intensidad)
    canvas_intensidad.get_tk_widget().pack(fill="both", expand=True)

    # Funciones internas de actualización
    def actualizar_histograma():
        """
        Actualiza el histograma promedio de los canales de color (RGB) en 
        tiempo real.
        """
        global task_histograma
        if streaming and imagen_capturada:
            ax_histograma.clear()
            rgb_array = np.array(imagen_capturada)
            r_values = np.mean(rgb_array[:, :, 0], axis=0)
            g_values = np.mean(rgb_array[:, :, 1], axis=0)
            b_values = np.mean(rgb_array[:, :, 2], axis=0)
            intensity_values = (r_values + g_values + b_values) / 3
            x = np.arange(rgb_array.shape[1])

            # Dibujar líneas de color
            ax_histograma.plot(x, r_values, color='red', label='Rojo')
            ax_histograma.plot(x, g_values, color='green', label='Verde')
            ax_histograma.plot(x, b_values, color='blue', label='Azul')
            ax_histograma.plot(x, intensity_values, color='black', label='Intensidad')

            # Configurar la gráfica
            ax_histograma.set_title("Histograma Promedio")
            ax_histograma.set_xlabel("Posición X del Stream")
            ax_histograma.set_ylabel("Valor Promedio")
            ax_histograma.legend()
            ax_histograma.grid(True)

            # Dibujar en el canvas
            canvas_histograma.draw()

        # Programar la siguiente actualización
        task_histograma = root.after(100, actualizar_histograma)

    def actualizar_intensidad():
        """
        Actualiza la gráfica de intensidad en escala de grises en tiempo real.
        La línea es completamente negra.
        """
        global task_intensidad
        if streaming and imagen_capturada:
            ax_intensidad.clear()
            gray_image = imagen_capturada.convert('L')  # Convertir a escala de grises
            gray_array = np.array(gray_image)  # Convertir a matriz NumPy
            intensity_profile = np.mean(gray_array, axis=0)  # Perfil de intensidad promedio
            x = np.arange(len(intensity_profile))  # Coordenadas X

            # Dibujar la línea en negro
            ax_intensidad.plot(x, intensity_profile, color='black', label='Intensidad')

            # Configurar la gráfica
            ax_intensidad.set_title("Perfil de Intensidad")
            ax_intensidad.set_xlabel("Posición X del Stream")
            ax_intensidad.set_ylabel("Intensidad")
            ax_intensidad.legend()
            ax_intensidad.grid(True)

            # Dibujar en el canvas
            canvas_intensidad.draw()

        # Programar la siguiente actualización
        task_intensidad = root.after(100, actualizar_intensidad)



    # Función para guardar las gráficas
    def guardar_graficas():
        """
        Guarda las gráficas del histograma y de intensidad como imágenes PNG
        en la carpeta 'Capturas'. Si la carpeta no existe, se crea.
        """
        # Crear carpeta si no existe
        carpeta_capturas = "Capturas"
        if not os.path.exists(carpeta_capturas):
            os.makedirs(carpeta_capturas)
            print(f"Carpeta '{carpeta_capturas}' creada.")

        # Generar nombres únicos para las gráficas
        hora_actual = datetime.now().strftime("%H-%M-%S")
        archivo_histograma = os.path.join(carpeta_capturas, f"Captura_Histograma_{hora_actual}.png")
        archivo_intensidad = os.path.join(carpeta_capturas, f"Captura_Intensidad_{hora_actual}.png")

        # Guardar las gráficas en la carpeta
        fig_histograma.savefig(archivo_histograma)
        fig_intensidad.savefig(archivo_intensidad)
        print(f"Gráficas guardadas como '{archivo_histograma}' y '{archivo_intensidad}'.")

    # Cancelar tareas al cerrar la ventana
    def on_close():
        global task_histograma, task_intensidad
        if task_histograma:
            root.after_cancel(task_histograma)
        if task_intensidad:
            root.after_cancel(task_intensidad)
        ventana_tabs.destroy()

    ventana_tabs.protocol("WM_DELETE_WINDOW", on_close)

    # Botón para guardar las gráficas
    boton_guardar = Button(ventana_tabs, text="Guardar Gráficas", command=guardar_graficas)
    boton_guardar.pack(side="bottom", pady=10)

    # Iniciar tareas de actualización
    actualizar_histograma()
    actualizar_intensidad()

# =============================================================================
# Cierre del programa al cerrar la GUI principal
# =============================================================================

def cerrar_programa():
    """
    Cierra el programa correctamente al cerrar la ventana principal.
    Detiene el stream si está activo y destruye la ventana.
    """
    stop_stream()
    root.destroy()
    print("Programa finalizado.")

# =============================================================================
# Interfaz gráfica principal
# =============================================================================

root = Tk()
root.title("Stream ESP32-CAM y Procesamiento de Imágenes")
root.geometry("1000x600")
root.protocol("WM_DELETE_WINDOW", cerrar_programa)  # Cerrar programa al cerrar la GUI

# Botones
frame_botones = Frame(root)
frame_botones.pack(side="left", padx=10, pady=10)
boton_iniciar = Button(frame_botones, text="Iniciar Stream", command=start_stream)
boton_iniciar.pack(pady=5)
boton_detener = Button(frame_botones, text="Detener Stream", command=stop_stream)
boton_detener.pack(pady=5)
boton_analisis = Button(frame_botones, text="Análisis en Tiempo Real", command=abrir_ventanas, state="disabled")
boton_analisis.pack(pady=5)

# Label para el video
video_label = Label(root, width=640, height=480, bg="black")
video_label.pack(side="right", padx=10, pady=10)

# Ejecutar la interfaz
root.mainloop()
