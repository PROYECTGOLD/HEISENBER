from flask import Flask, request, jsonify
from moviepy.editor import TextClip, CompositeVideoClip, ColorClip
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import os

app = Flask(__name__)

# Cargar credenciales de servicio
SERVICE_ACCOUNT_FILE = "heisenberg-463407-63df8f900747.json"
SCOPES = ["https://www.googleapis.com/auth/drive"]

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)
drive_service = build("drive", "v3", credentials=credentials)

@app.route("/")
def home():
    return "Servidor activo ✅"

@app.route("/generar_video", methods=["POST"])
def generar_video():
    data = request.get_json()
    idea = data.get("idea", "Sin idea")
    text = data.get("text", "Sin texto")

    # Crear video con MoviePy
    width, height = 1080, 1920  # Formato vertical
    color_clip = ColorClip(size=(width, height), color=(0, 0, 0), duration=10)

    text_clip = TextClip(text, fontsize=60, color='white', size=(width - 100, None), method='caption')
    text_clip = text_clip.set_position('center').set_duration(10)

    final = CompositeVideoClip([color_clip, text_clip])

    filename = f"video_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
    final.write_videofile(filename, fps=24)

    # Subir a Google Drive
    file_metadata = {
        'name': filename,
        'parents': ['root']  # O especificar carpeta con su ID
    }
    media = MediaFileUpload(filename, mimetype='video/mp4')
    file = drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()

    # Hacerlo público
    drive_service.permissions().create(
        fileId=file['id'],
        body={"role": "reader", "type": "anyone"},
    ).execute()

    video_url = f"https://drive.google.com/uc?id={file['id']}"

    # Eliminar el archivo local
    os.remove(filename)

    return jsonify({"status": "ok", "video_url": video_url})

if __name__ == "__main__":
    app.run(debug=True)
