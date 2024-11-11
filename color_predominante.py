from PIL import Image
import numpy as np
from collections import Counter
import matplotlib.pyplot as plt

# Ruta de la imagen
image_path = r'C:\Users\thebl\OneDrive\Escritorio\Espectrofotometro_Celular\recorte_referencia_verde.png'
image = Image.open(image_path).convert('RGB')  # Convertir a RGB para eliminar canal alfa si existe

# Convertir la imagen a un array numpy
image_np = np.array(image)
height, width, _ = image_np.shape

# Lista para almacenar el color más común en cada columna
most_common_colors = []

# Analizar cada columna de la imagen
for col in range(width):
    # Extraer los píxeles de la columna actual
    column_pixels = image_np[:, col]
    
    # Contar los colores en la columna
    color_counts = Counter(map(tuple, column_pixels))  # Convertir cada píxel a tupla para contar
    most_common_color = color_counts.most_common(1)[0][0]  # Obtener el color más común
    
    # Agregar el color más común de la columna a la lista
    most_common_colors.append(most_common_color)

# Crear una imagen para visualizar los colores más comunes de cada columna
most_common_image = np.array(most_common_colors * height, dtype=np.uint8).reshape(height, width, 3)

# Mostrar la imagen original y la visualización de colores más comunes por columna
plt.figure(figsize=(10, 5))

# Imagen original
plt.subplot(1, 2, 1)
plt.imshow(image)
plt.title('Imagen Original')
plt.axis('off')

# Visualización del color más común por columna
plt.subplot(1, 2, 2)
plt.imshow(most_common_image)
plt.title('Color Más Común en Cada Columna')
plt.axis('off')

plt.show()
