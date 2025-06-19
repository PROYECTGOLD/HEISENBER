import os
from flask import Flask, request, jsonify
from moviepy.editor import CompositeVideoClip, ColorClip, ImageClip
import datetime
from PIL import Image, ImageDraw, ImageFont
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

app = Flask(__name__)

# Ruta al archivo de credenciales montado en Render
CREDENTIALS_PATH = "/etc/secrets/heisenberg-credentials.json"
SCOPES = ["https://www.googleapis.com/auth/drive.file"]
credentials = service_account.Credentials.from_service_account_file(
    CREDENTIALS_PATH, scopes=SCOPES
)
drive_service = build("drive", "v3", credentials=credentials)

@app.route("/generar_video", methods=["POST"])
def generar_video():
    try:
        data = request.get_json()
        texto = data.get("text", "Texto por defecto")

        # 🖼️ Crear imagen con texto usando PIL
        img = Image.new("RGB", (720, 1280), color=(0, 0, 0))
        draw = ImageDraw.Draw(img)
        font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        font = ImageFont.truetype(font_path, 60)

        # Calcular posición centrada
        text_width, text_height = font.getsize(texto)
        x = (img.width - text_width) / 2
        y = (img.height - text_height) / 2
        draw.text((x, y), texto, font=font, fill=(255, 255, 255))

        # Guardar imagen temporal
        image_filename = "frame.png"
        img.save(image_filename)

        # 🎥 Convertir imagen en clip de video
        clip = ImageClip(image_filename, duration=7)
        final = CompositeVideoClip([clip])
        output_filename = f"video_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.mp4"
        final.write_videofile(
            output_filename,
            fps=24,
            codec="libx264",
            bitrate="800k",
            audio=False,
            threads=4
        )

        # ☁️ Subir a Google Drive
        file_metadata = {"name": output_filename, "mimeType": "video/mp4"}
        media = MediaFileUpload(output_filename, mimetype="video/mp4")
        file = drive_service.files().create(
            body=file_metadata, media_body=media, fields="id"
        ).execute()
        file_id = file["id"]

        # 🌐 Hacerlo público
        drive_service.permissions().create(
            fileId=file_id,
            body={"type": "anyone", "role": "reader"}
        ).execute()

        # 📎 Devolver URL
        video_url = f"https://drive.google.com/uc?id={file_id}"
        return jsonify({"status": "ok", "video_url": video_url})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# 🔥 Iniciar Flask (modo desarrollo)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))







