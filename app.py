from flask import Flask, request, jsonify
import os
from moviepy.editor import TextClip, CompositeVideoClip
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

app = Flask(__name__)

# Credenciales y configuración de Google Drive
SERVICE_ACCOUNT_FILE = "heisenberg-463407-63df8f900747.json"
SCOPES = ["https://www.googleapis.com/auth/drive.file"]
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
    idea = data.get("idea", "")
    text = data.get("text", "")

    # Crear video simple con texto
    clip = TextClip(txt=text, fontsize=70, color='white', size=(720, 1280))
    clip = clip.set_duration(10)
    video_path = "output.mp4"
    clip.write_videofile(video_path, fps=24)

    # Subir a Google Drive
    file_metadata = {"name": f"{idea}.mp4", "mimeType": "video/mp4"}
    media = MediaFileUpload(video_path, mimetype="video/mp4")
    file = drive_service.files().create(body=file_metadata, media_body=media, fields="id").execute()
    file_id = file.get("id")
    drive_service.permissions().create(fileId=file_id, body={"role": "reader", "type": "anyone"}).execute()
    video_url = f"https://drive.google.com/file/d/{file_id}/view"

    return jsonify({"status": "ok", "video_url": video_url})
