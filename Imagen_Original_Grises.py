from PIL import Image
import matplotlib.pyplot as plt

# Ruta de la imagen
image_path = r'C:\Users\thebl\OneDrive\Escritorio\Espectrofotometro_Celular\recorte_luz_roja2.png'
image = Image.open(image_path)

# Convertir la imagen a escala de grises
gray_image = image.convert('L')

# Mostrar ambas imágenes: original y escala de grises
plt.figure(figsize=(10, 5))

# Imagen original
plt.subplot(1, 2, 1)
plt.imshow(image)
plt.title('Imagen Original')
plt.axis('off')

# Imagen en escala de grises
plt.subplot(1, 2, 2)
plt.imshow(gray_image, cmap='gray')
plt.title('Imagen en Escala de Grises')
plt.axis('off')

plt.show()
