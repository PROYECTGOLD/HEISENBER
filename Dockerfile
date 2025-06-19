FROM python:3.10-slim

# Instalar dependencias necesarias: ffmpeg e imagemagick
RUN apt-get update && apt-get install -y ffmpeg imagemagick

# Arreglar la política restrictiva de ImageMagick
RUN sed -i 's/rights="none" pattern="PDF"/rights="read|write" pattern="PDF"/' /etc/ImageMagick-6/policy.xml \
 && sed -i 's/rights="none" pattern="LABEL"/rights="read|write" pattern="LABEL"/' /etc/ImageMagick-6/policy.xml \
 && sed -i 's/rights="none" pattern="TXT"/rights="read|write" pattern="TXT"/' /etc/ImageMagick-6/policy.xml

WORKDIR /app

# Copiar requirements e instalar dependencias
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copiar el código fuente
COPY . .

# Ejecutar la app
CMD gunicorn --bind 0.0.0.0:${PORT} app:app
