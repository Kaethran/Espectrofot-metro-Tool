import cv2
from tkinter import Tk, Button, Label
from PIL import Image, ImageTk

# Dirección del ESP32-CAM
url = "http://192.168.100.13:81/stream"

# Variables globales
cap = None
streaming = False

def start_stream():
    """Inicia o reanuda el stream."""
    global cap, streaming
    if not streaming:
        cap = cv2.VideoCapture(url)
        streaming = True
        update_frame()
        print("Stream iniciado automáticamente.")

def update_frame():
    """Actualiza el frame en la ventana de Tkinter."""
    global cap, streaming
    if streaming and cap is not None:
        ret, frame = cap.read()
        if ret:
            # Convertir el frame para Tkinter
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)

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
        print("Stream detenido.")

def close_application():
    """Cierra la aplicación."""
    stop_stream()
    root.quit()
    print("Aplicación cerrada.")

# Crear la ventana principal
root = Tk()
root.title("Stream ESP32-CAM")

# Etiqueta para el video
video_label = Label(root)
video_label.pack()

# Botón para iniciar/reanudar el stream
start_button = Button(root, text="Reanudar Stream", command=start_stream, height=2, width=20)
start_button.pack(pady=10)

# Botón para detener el stream
stop_button = Button(root, text="Detener Stream", command=stop_stream, height=2, width=20)
stop_button.pack(pady=10)

# Botón para cerrar la aplicación
close_button = Button(root, text="Cerrar Aplicación", command=close_application, height=2, width=20)
close_button.pack(pady=10)

# Iniciar el stream automáticamente
start_stream()

# Ejecutar la interfaz gráfica
root.mainloop()
