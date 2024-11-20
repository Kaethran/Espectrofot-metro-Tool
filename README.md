# Proyecto: Espectrofotómetro Digital En Tiempo Real Para Uso Didáctico

**Autores:**
- Luis Octavio Pimienta Murillo
- Alejandra Ochoa Gutiérrez

## Descripción
Este proyecto consiste en un programa para capturar, visualizar y analizar 
datos de intensidad de luz en tiempo real usando una ESP32-CAM. La interfaz gráfica 
permite realizar análisis como histogramas y perfiles de intensidad.

---

## Requisitos del Sistema
- Sistema operativo: Windows 10 o superior.
- Python 3.12 (solo para desarrollo, no necesario si usas el ejecutable).
- Conexión a una ESP32-CAM en la red local.

---

## Instrucciones
1. Ejecute el archivo `ESP32_CAM_GUI_DINAMICA.exe`.
2. Este ejecutable está configurado específicamente para la dirección IP 
   usada durante su creación. Si la ESP32-CAM tiene una IP diferente, 
   será necesario modificar el código fuente y generar un nuevo ejecutable.
3. Utilice los botones de la interfaz gráfica para:
   - Iniciar el stream de video.
   - Recortar y analizar el video en tiempo real.
   - Generar gráficos como histogramas y perfiles de intensidad.

---

## Estructura del Proyecto
- `ESP32_CAM_GUI_DINAMICA.exe`: Archivo ejecutable principal (no incluido en el repositorio).
- `README.md`: Este archivo con información del proyecto.
- `templates/portada_Fotónica.png`: Imagen utilizada en la interfaz gráfica.

---

## Notas
- Este proyecto actualmente requiere modificar manualmente la dirección IP de la ESP32-CAM en el código fuente.
- **Futuras versiones**: Se planea agregar la funcionalidad de ingresar la dirección IP manualmente desde la interfaz del programa, para evitar la necesidad de modificar el código.
- Si la IP de la ESP32-CAM cambia, será necesario modificar el código fuente 
  en la variable `url` y generar un nuevo ejecutable.
- Este proyecto fue desarrollado como herramienta didáctica para análisis espectrofotométrico.
