import os
from flask import Flask, request, jsonify
from moviepy.editor import TextClip, CompositeVideoClip, ColorClip
import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

app = Flask(__name__)

# Ruta al archivo de credenciales (Render lo monta en /etc/secrets/)
CREDENTIALS_PATH = "/etc/secrets/heisenberg-credentials.json"

# Autenticación con Google Drive
SCOPES = ["https://www.googleapis.com/auth/drive.file"]
credentials = service_account.Credentials.from_service_account_file(
    CREDENTIALS_PATH, scopes=SCOPES
)
drive_service = build("drive", "v3", credentials=credentials)


@app.route("/generar_video", methods=["POST"])
def generar_video():
    try:
        data = request.get_json()
        idea = data.get("idea", "IDEA")
        texto = data.get("text", "Texto por defecto")

        # 🎥 Generar clip de texto
        clip = TextClip(
            txt=texto,
            fontsize=70,
            color="white",
            size=(720, 1280),
            method="caption",
        ).set_duration(10)

        background = ColorClip(size=(720, 1280), color=(0, 0, 0)).set_duration(10)

        final = CompositeVideoClip([background, clip.set_position("center")])
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        output_filename = f"video_{timestamp}.mp4"
        final.write_videofile(output_filename, fps=24)

        # 📤 Subir a Google Drive
        file_metadata = {"name": output_filename, "mimeType": "video/mp4"}
        media = MediaFileUpload(output_filename, mimetype="video/mp4")

        file = drive_service.files().create(
            body=file_metadata, media_body=media, fields="id"
        ).execute()

        file_id = file.get("id")

        # 🌍 Hacer el archivo público
        drive_service.permissions().create(
            fileId=file_id,
            body={"type": "anyone", "role": "reader"},
        ).execute()

        # 🔗 Generar enlace público
        video_url = f"https://drive.google.com/uc?id={file_id}"
        return jsonify({"status": "ok", "video_url": video_url})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# 🚀 Ejecutar con Gunicorn en producción
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))




