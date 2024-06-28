# Usar una imagen base de Python
FROM python:3.8

# Establecer un directorio de trabajo
WORKDIR /app

# Copiar los archivos requirements.txt y ejecutar pip install
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Copiar el resto del código de la aplicación al contenedor
COPY . .

# Exponer el puerto en el que se ejecutará la aplicación
EXPOSE 3000

# Command to start the application
CMD ["uvicorn", "App:app", "--host", "0.0.0.0", "--port", "3000"]



