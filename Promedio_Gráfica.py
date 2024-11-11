from PIL import Image
import numpy as np
import matplotlib.pyplot as plt

# Ruta de la imagen
image_path = r'C:\Users\thebl\OneDrive\Escritorio\Espectrofotometro_Celular\recorte_rojo_prueba.png'
image = Image.open(image_path).convert('RGB')  # Convertir a RGB para eliminar canal alfa si existe

# Convertir la imagen a un array numpy
image_np = np.array(image)
height, width, _ = image_np.shape

# Convertir la imagen a escala de grises para calcular la intensidad
gray_image = np.mean(image_np, axis=2)  # Promedio de los canales RGB para escala de grises

# Calcular la intensidad promedio en cada columna
column_intensity = gray_image.mean(axis=0)

# Graficar la intensidad promedio de cada columna
plt.figure(figsize=(10, 5))
plt.plot(column_intensity, color='blue', label='Intensidad Promedio')
plt.title('Intensidad Promedio por Columna')
plt.xlabel('Columna')
plt.ylabel('Intensidad Promedio (0-255)')
plt.legend()
plt.grid(True)
plt.show()
