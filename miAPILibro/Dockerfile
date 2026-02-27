FROM python:3.12-slim

## creamos la carpeta de trabajo del contenedor
WORKDIR /app

##Copiamos los requerimientos del servidor
COPY requirements.txt . 

##Instalamos los requerimientos
RUN pip install --no-cache-dir -r requirements.txt

#copiar el codigo de nuestra API para que habite en el contenedor
COPY ./app ./app

#Exponer el puerto con el cual estara trabajando el contenedor
EXPOSE 5000

#Comando de ejecucion FASTAPI
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5000", "--reload"]
