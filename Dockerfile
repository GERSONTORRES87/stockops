# Imagen base: Python 3.12 en versión ligera
FROM python:3.12-slim

# Carpeta de trabajo dentro del contenedor
WORKDIR /app

# Primero las dependencias (aprovecha la caché de Docker)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Luego el código de la aplicación
COPY . .

# Puerto en el que escucha Flask
EXPOSE 5000

# Comando que se ejecuta al iniciar el contenedor
CMD ["python", "app.py"]
