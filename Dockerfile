FROM python:3.10-slim

# Evitar mensajes interactivos de apt
ENV DEBIAN_FRONTEND=noninteractive

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsm6 \
    libxext6 \
    && apt-get clean

# Crear directorio de trabajo
WORKDIR /app

# Copiar requirements y app
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

# Puerto y comando
ENV PORT=10000
CMD ["gunicorn", "--bind", "0.0.0.0:$PORT", "app:app"]