import cv2
from tkinter import Tk, Button, Label, Frame, Canvas, Toplevel, ttk
from PIL import Image, ImageTk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.colors as mcolors

# Dirección del ESP32-CAM
url = "http://192.168.100.13:81/stream"

# Variables globales
cap = None
streaming = False
imagen_capturada = None
task_intensidad = None
task_histograma = None

# Funciones del stream
def start_stream():
    """Inicia o reanuda el stream."""
    global cap, streaming
    if not streaming:
        cap = cv2.VideoCapture(url)
        streaming = True
        boton_analisis.config(state="normal")  # Habilitar análisis en tiempo real
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
        boton_analisis.config(state="disabled")  # Deshabilitar análisis en tiempo real
        print("Stream detenido.")

# Función para abrir la ventana de histogramas y gráficos
def abrir_ventanas():
    """Abre dos pestañas: una para el histograma y otra para graficar intensidad."""
    if not streaming:
        print("El stream debe estar iniciado para acceder a esta funcionalidad.")
        return

    ventana_tabs = Toplevel(root)
    ventana_tabs.title("Análisis en Tiempo Real")
    ventana_tabs.geometry("800x600")
    
    # Crear las pestañas
    tabs = ttk.Notebook(ventana_tabs)
    tab_histograma = ttk.Frame(tabs)
    tab_intensidad = ttk.Frame(tabs)
    
    tabs.add(tab_histograma, text="Histograma")
    tabs.add(tab_intensidad, text="Graficar Intensidad")
    tabs.pack(expand=1, fill="both")

    # Crear figuras para matplotlib
    fig_histograma, ax_histograma = plt.subplots(figsize=(7, 5))
    fig_intensidad, ax_intensidad = plt.subplots(figsize=(7, 5))

    # Canvas para incrustar las figuras
    canvas_histograma = FigureCanvasTkAgg(fig_histograma, master=tab_histograma)
    canvas_histograma.get_tk_widget().pack(fill="both", expand=True)

    canvas_intensidad = FigureCanvasTkAgg(fig_intensidad, master=tab_intensidad)
    canvas_intensidad.get_tk_widget().pack(fill="both", expand=True)

    # Variables globales para tareas
    global task_histograma, task_intensidad

    def actualizar_histograma():
        """Actualiza el histograma promedio en tiempo real."""
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
            ax_histograma.plot(x, intensity_values, color='black', label='Intensidad', linestyle='--', alpha=0.7)
            ax_histograma.set_title('Histograma Promedio en Tiempo Real')
            ax_histograma.set_xlabel('Posición en X')
            ax_histograma.set_ylabel('Valor Promedio')
            ax_histograma.legend()
            ax_histograma.grid(True)
            canvas_histograma.draw()

        task_histograma = root.after(100, actualizar_histograma)

    def actualizar_intensidad():
        """Actualiza la gráfica de intensidad en tiempo real."""
        global task_intensidad
        if streaming and imagen_capturada:
            ax_intensidad.clear()
            gray_image = imagen_capturada.convert('L')
            gray_array = np.array(gray_image)
            intensity_profile = np.mean(gray_array, axis=0)
            x = np.arange(len(intensity_profile))
            colors = ["#8B00FF", "#4B0082", "#0000FF", "#00FF00", "#FFFF00", "#FF7F00", "#FF0000"]
            cmap = mcolors.LinearSegmentedColormap.from_list("spectrum", colors)

            scatter = ax_intensidad.scatter(x, intensity_profile, c=x, cmap=cmap, marker='o', edgecolor='none')
            ax_intensidad.plot(intensity_profile, color='black', alpha=0.3)
            ax_intensidad.set_title('Perfil de Intensidad en Tiempo Real')
            ax_intensidad.set_xlabel('Posición (longitud de onda aproximada)')
            ax_intensidad.set_ylabel('Intensidad')
            ax_intensidad.grid(True)
            canvas_intensidad.draw()

        task_intensidad = root.after(100, actualizar_intensidad)

    # Cancelar tareas al cerrar la ventana
    def on_close():
        global task_histograma, task_intensidad
        if task_histograma:
            root.after_cancel(task_histograma)
        if task_intensidad:
            root.after_cancel(task_intensidad)
        ventana_tabs.destroy()

    # Asociar el cierre de ventana con la función
    ventana_tabs.protocol("WM_DELETE_WINDOW", on_close)

    # Iniciar actualizaciones
    actualizar_histograma()
    actualizar_intensidad()

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

boton_analisis = Button(frame_botones, text="Análisis en Tiempo Real", command=abrir_ventanas, state="disabled")
boton_analisis.pack(pady=5)

# Sección del stream
video_label = Label(root, width=640, height=480, bg="black")
video_label.pack(side="right", padx=10, pady=10)

# Ejecutar la interfaz gráfica
root.mainloop()
