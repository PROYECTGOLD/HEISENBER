from flask import Flask, request, jsonify
from moviepy.editor import TextClip, CompositeVideoClip, ColorClip
import os
import tempfile
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

os.environ["IMAGEMAGICK_BINARY"] = "/usr/bin/convert"

app = Flask(__name__)

# ✅ Autenticación con Google Drive
SERVICE_ACCOUNT_FILE = "/etc/secrets/heisenberg-credentials.json"
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

    try:
        # 🖋️ Crear fondo + texto
        clip = TextClip(text, fontsize=60, color="white", font="DejaVu-Sans", size=(720, 1280)).set_duration(10)
        background = ColorClip(size=(720, 1280), color=(0, 0, 0), duration=10)
        video = CompositeVideoClip([background, clip.set_position("center")])

        # 🎞️ Guardar temporalmente
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
            video_path = tmp.name
        video.write_videofile(video_path, fps=24)

        # ☁️ Subir a Google Drive
        file_metadata = {"name": f"{idea}.mp4", "mimeType": "video/mp4"}
        media = MediaFileUpload(video_path, mimetype="video/mp4")
        file = drive_service.files().create(body=file_metadata, media_body=media, fields="id").execute()
        file_id = file.get("id")

        # 🌐 Hacer público
        drive_service.permissions().create(
            fileId=file_id,
            body={"type": "anyone", "role": "reader"},
        ).execute()

        video_url = f"https://drive.google.com/uc?id={file_id}"
        return jsonify({"status": "ok", "video_url": video_url})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
