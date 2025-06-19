# CTM210183 - Servidor Flask con generación de videos y subida a Google Drive (Render + Cuenta de Servicio)

Este proyecto despliega un servidor Flask en Render que:
- Genera un video vertical desde texto (con MoviePy)
- Lo sube automáticamente a Google Drive usando una cuenta de servicio
- Devuelve un enlace público al video (`video_url`)

---

## 🚀 Despliegue en Render

### 1. Subir a GitHub

1. Descomprime el archivo `video_server_render_drive_ready.zip`
2. Sube el contenido a un repositorio nuevo en GitHub (ej: `CTM210183`)

### 2. Agrega tu archivo de cuenta de servicio

Sube el archivo que descargaste desde Google Cloud (tipo `heisenberg-xxxxxx.json`) al mismo repositorio y renómbralo como:

```
service_account.json
```

Debe quedar en la **raíz del proyecto**, junto a `app.py`

### 3. Conéctalo en Render

1. Ve a [https://render.com](https://render.com)
2. Crea un nuevo **Web Service**
3. Selecciona "Deploy from GitHub" y elige tu repo
4. Render detectará `render.yaml` y lo desplegará automáticamente

---

## 🧪 Uso de la API

### `POST /generar_video`

Envía un JSON con la idea y el texto:

```json
{
  "idea": "La idea del video",
  "text": "El texto que aparecerá"
}
```

### 📥 Respuesta:

```json
{
  "status": "ok",
  "video_url": "https://drive.google.com/uc?id=..."
}
```

---

## 📂 Archivos importantes

- `app.py`: Lógica del servidor + subida a Drive
- `service_account.json`: Clave privada de cuenta de servicio (NO compartir)
- `render.yaml`: Script de despliegue automático
- `requirements.txt`: Dependencias

---

## 🛟 Requisitos

- Cuenta de Google Cloud con la **Drive API habilitada**
- Archivo `service_account.json` generado
- Carpeta de destino en Drive (opcional, si compartes el acceso)

---

CTM210183 - Desarrollado por Carlos con ayuda de IA 🧠🚀