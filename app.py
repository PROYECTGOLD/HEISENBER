from flask import Flask, request, jsonify
from moviepy.editor import ImageClip, concatenate_videoclips, AudioFileClip
import os
import datetime
import tempfile
import uuid
import json
import io

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

app = Flask(__name__)

# Ruta al archivo de credenciales en Render
CREDENTIALS_PATH = "/etc/secrets/heisenberg-credentials.json"
FOLDER_ID = "1952GPiJ002KyA8hYkEnt7nvSSGAHweoN"  # Reemplaza si usas otra carpeta

def upload_to_drive(filepath, filename):
    credentials = service_account.Credentials.from_service_account_file(CREDENTIALS_PATH, scopes=["https://www.googleapis.com/auth/drive"])
    service = build("drive", "v3", credentials=credentials)

    file_metadata = {
        "name": filename,
        "parents": [FOLDER_ID]
    }
    media = MediaFileUpload(filepath, mimetype="video/mp4")

    uploaded = service.files().create(body=file_metadata, media_body=media, fields="id").execute()
    file_id = uploaded.get("id")

    return f"https://drive.google.com/file/d/{file_id}/view"

@app.route('/generar_video', methods=['POST'])
def generar_video():
    try:
        data = request.get_json()

        idea = data.get("idea")
        imagenes = data.get("imagenes")

        if not idea or not imagenes or len(imagenes) < 1:
            return jsonify({"error": "Faltan datos requeridos (idea, imagenes)"}), 400

        clips = []
        duration = 4  # 3 imágenes * 4s = 12s

        for img_url in imagenes:
            clip = ImageClip(img_url, duration=duration).resize(height=1920).set_position("center").set_duration(duration)
            clips.append(clip)

        final_video = concatenate_videoclips(clips, method="compose")

        # Opcional: Agregar música
        if os.path.exists("music.mp3"):
            audio = AudioFileClip("music.mp3").volumex(0.2)
            final_video = final_video.set_audio(audio)

        output_filename = f"video_{uuid.uuid4().hex[:8]}.mp4"
        output_path = os.path.join(tempfile.gettempdir(), output_filename)
        final_video.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac")

        video_url = upload_to_drive(output_path, output_filename)

        return jsonify({"video_url": video_url}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000)







