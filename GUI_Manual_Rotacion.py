import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

def cargar_imagen():
    global imagen_original, imagen_mostrada, imagen_actual, angulo_acumulado
    ruta_imagen = filedialog.askopenfilename(filetypes=[("Imágenes", "*.png;*.jpg;*.jpeg;*.bmp")])
    if ruta_imagen:
        imagen_original = Image.open(ruta_imagen)
        imagen_original.thumbnail((500, 500))
        imagen_mostrada = imagen_original.copy()
        imagen_actual = imagen_original.copy()
        angulo_acumulado = 0
        mostrar_imagen(imagen_mostrada)

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
            
            # Recortar y actualizar la imagen actual
            imagen_actual = imagen_actual.crop((x0, y0, x1, y1))
            mostrar_imagen(imagen_actual)
        
        modo_recorte = False
        boton_recortar.config(text="Recortar Imagen", state="normal")
        ventana.config(cursor="")
        etiqueta_imagen.delete(rectangulo)

def mostrar_imagen(imagen):
    global imagen_tk
    imagen_tk = ImageTk.PhotoImage(imagen)
    etiqueta_imagen.config(width=imagen.width, height=imagen.height)
    etiqueta_imagen.create_image(0, 0, anchor="nw", image=imagen_tk)

def rotar_imagen():
    global imagen_actual, angulo_acumulado
    try:
        # Validar que el ángulo es un número y está en el rango adecuado
        angulo = int(entry_angulo.get())
        if 0 <= angulo <= 360:
            angulo_acumulado = (angulo_acumulado + angulo) % 360  # Acumula el ángulo
            slider_rotacion.set(angulo_acumulado)

            # Rota la imagen dentro de su marco original, sin expandir el fondo
            imagen_rotada = imagen_actual.rotate(angulo_acumulado, expand=False)
            imagen_actual = imagen_rotada  # Actualiza la imagen actual con la rotada
            mostrar_imagen(imagen_actual)
        else:
            messagebox.showerror("Error", "El ángulo debe estar entre 0 y 360.")
    except ValueError:
        messagebox.showerror("Error", "Ingrese un ángulo válido (número entre 0 y 360).")

def actualizar_angulo_desde_slider(value):
    entry_angulo.delete(0, tk.END)
    entry_angulo.insert(0, str(int(float(value))))

def restaurar_imagen_original():
    global imagen_actual, angulo_acumulado
    imagen_actual = imagen_original.copy()  # Restaura a la imagen original sin transformaciones
    angulo_acumulado = 0  # Reinicia el ángulo acumulado
    mostrar_imagen(imagen_actual)

# Configuración de la ventana
ventana = tk.Tk()
ventana.title("Cargar, Rotar y Recortar Imagen Visualmente")
ventana.geometry("600x750")

# Variables globales
imagen_original = None
imagen_mostrada = None
imagen_actual = None
x_inicial = y_inicial = 0
rectangulo = None
modo_recorte = False
angulo_acumulado = 0

# Botón para cargar la imagen
boton_cargar = tk.Button(ventana, text="Cargar Imagen", command=cargar_imagen)
boton_cargar.pack(pady=10)

# Control deslizante para rotar la imagen
slider_rotacion = tk.Scale(ventana, from_=0, to=360, orient="horizontal", label="Ángulo de Rotación",
                           command=actualizar_angulo_desde_slider)
slider_rotacion.pack()

# Entrada de texto para ingresar el ángulo directamente
frame_angulo = tk.Frame(ventana)
frame_angulo.pack(pady=5)
label_angulo = tk.Label(frame_angulo, text="Ángulo de rotación:")
label_angulo.pack(side="left")
entry_angulo = tk.Entry(frame_angulo, width=5)
entry_angulo.pack(side="left")
entry_angulo.insert(0, "0")

# Botón para aplicar la rotación
boton_rotar = tk.Button(ventana, text="Aplicar Rotación", command=rotar_imagen)
boton_rotar.pack(pady=10)

# Botón para activar el modo de recorte
boton_recortar = tk.Button(ventana, text="Recortar Imagen", command=activar_recorte)
boton_recortar.pack(pady=10)

# Botón para restaurar la imagen original
boton_restaurar = tk.Button(ventana, text="Restaurar Imagen Original", command=restaurar_imagen_original)
boton_restaurar.pack(pady=10)

# Canvas para mostrar y dibujar sobre la imagen
etiqueta_imagen = tk.Canvas(ventana, width=500, height=500)
etiqueta_imagen.pack()
etiqueta_imagen.bind("<Button-1>", iniciar_seleccion)       
etiqueta_imagen.bind("<B1-Motion>", actualizar_seleccion)   
etiqueta_imagen.bind("<ButtonRelease-1>", terminar_seleccion) 

ventana.mainloop()
