from flask import Flask, request, jsonify
from moviepy.editor import TextClip, CompositeVideoClip
import os
import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

app = Flask(__name__)

# Ruta al archivo JSON de credenciales de Google Drive (debe estar en el mismo repo)
SERVICE_ACCOUNT_FILE = 'heisenberg-463407-63df8f900747.json'
SCOPES = ['https://www.googleapis.com/auth/drive.file']

def subir_a_drive(nombre_archivo_local):
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('drive', 'v3', credentials=credentials)

    file_metadata = {
        'name': os.path.basename(nombre_archivo_local),
        'mimeType': 'video/mp4'
    }
    media = MediaFileUpload(nombre_archivo_local, mimetype='video/mp4')
    archivo = service.files().create(body=file_metadata, media_body=media, fields='id').execute()

    # Hacer el archivo público
    service.permissions().create(fileId=archivo['id'], body={
        'role': 'reader',
        'type': 'anyone'
    }).execute()

    video_url = f"https://drive.google.com/file/d/{archivo['id']}/view"
    return video_url

@app.route("/")
def home():
    return "Servidor activo ✅"

@app.route("/generar_video", methods=["POST"])
def generar_video():
    data = request.get_json()
    idea = data.get("idea", "Sin idea")
    texto = data.get("text", "Texto por defecto")

    try:
        # Crear video simple
        clip = TextClip(texto, fontsize=60, color='white', size=(720, 1280), method='caption')
        clip = clip.set_duration(10)

        video = CompositeVideoClip([clip])
        nombre_archivo = f"video_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.mp4"
        video.write_videofile(nombre_archivo, fps=24)

        # Subir a Google Drive
        video_url = subir_a_drive(nombre_archivo)

        # Eliminar archivo local
        os.remove(nombre_archivo)

        return jsonify({"status": "ok", "video_url": video_url})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == "__main__":
    app.run(debug=True)
