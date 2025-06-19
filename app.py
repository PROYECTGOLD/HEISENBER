import os
import json
import tempfile
import random
import requests
from flask import Flask, request, jsonify
from moviepy.editor import *
from pydub import AudioSegment
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

app = Flask(__name__)

# Autenticación con Google Drive
SCOPES = ['https://www.googleapis.com/auth/drive.file']
SERVICE_ACCOUNT_FILE = '/etc/secrets/heisenberg-credentials.json'

credentials = Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
drive_service = build('drive', 'v3', credentials=credentials)

FOLDER_ID = '1952GPiJ002KyA8hYkEnt7nvSSGAHweoN'

@app.route("/")
def index():
    return "Servidor en producción con Gunicorn ✅"

@app.route("/generar_video", methods=["POST"])
def generar_video():
    data = request.get_json()
    idea = data.get("idea", "Idea sin nombre")
    imagenes = data.get("imagenes", [])

    if len(imagenes) < 3:
        return jsonify({"error": "Se requieren al menos 3 imágenes."}), 400

    clips = []
    duration = 4  # 4 segundos por imagen × 3 = 12s

    for url in imagenes[:3]:
        response = requests.get(url)
        temp_img = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
        temp_img.write(response.content)
        temp_img.close()

        img_clip = ImageClip(temp_img.name).set_duration(duration).resize(height=1080).set_position("center").set_fps(30)
        clips.append(img_clip)

    final_clip = concatenate_videoclips(clips, method="compose")

    # Música de fondo
    music_path = os.path.join("assets", "musica.mp3")
    if os.path.exists(music_path):
        music = AudioFileClip(music_path).subclip(0, final_clip.duration)
        final_clip = final_clip.set_audio(music)

    output_filename = f"video_{idea.replace(' ', '_')}.mp4"
    final_path = os.path.join(tempfile.gettempdir(), output_filename)
    final_clip.write_videofile(final_path, fps=30)

    # Subir a Google Drive
    file_metadata = {
        'name': output_filename,
        'parents': [FOLDER_ID]
    }
    media = MediaFileUpload(final_path, mimetype='video/mp4')
    uploaded_file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    video_id = uploaded_file.get('id')
    video_url = f"https://drive.google.com/file/d/{video_id}/view"

    return jsonify({"status": "ok", "video_url": video_url})





