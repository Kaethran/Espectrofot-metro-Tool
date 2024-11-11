from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import os

# Ruta de la imagen
image_path = r'C:\Users\thebl\OneDrive\Escritorio\Espectrofotometro_Celular\recorte_rojo_prueba.png'
image = Image.open(image_path)

# Extraer el nombre del archivo sin la ruta
filename = os.path.basename(image_path)

# Convertir la imagen a escala de grises para detectar la intensidad
gray_image = image.convert('L')
gray_array = np.array(gray_image)

# Calcular la intensidad promedio en el eje Y
intensity_profile = np.mean(gray_array, axis=0)

# Crear los valores del eje X de acuerdo al tamaño de la imagen
x = np.arange(len(intensity_profile))

# Crear un gradiente de colores para el espectro visible (de morado a rojo)
colors = ["#8B00FF", "#4B0082", "#0000FF", "#00FF00", "#FFFF00", "#FF7F00", "#FF0000"]
cmap = mcolors.LinearSegmentedColormap.from_list("spectrum", colors)

# Graficar el perfil de intensidad con el gradiente de color
plt.figure(figsize=(10, 6))
scatter = plt.scatter(x, intensity_profile, c=x, cmap=cmap, marker='o', edgecolor='none')
plt.plot(intensity_profile, color='black', alpha=0.3)  # Línea de guía en negro para la forma
plt.title(f'Perfil de Intensidad del Espectro - {filename}')
plt.xlabel('Posición (longitud de onda aproximada)')
plt.ylabel('Intensidad')

# Añadir una barra de color como referencia del espectro
plt.colorbar(scatter, orientation='horizontal', label='Color del espectro')
plt.grid(True)

plt.show()
