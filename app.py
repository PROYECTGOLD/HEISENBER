from flask import Flask, request, jsonify
from moviepy.editor import *
import os
import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests

app = Flask(__name__)

# Credenciales de Google Drive
scope = ["https://www.googleapis.com/auth/drive", "https://spreadsheets.google.com/feeds"]
credentials = ServiceAccountCredentials.from_json_keyfile_name("/etc/secrets/heisenberg-credentials.json", scope)
gc = gspread.authorize(credentials)

# Subir archivo a Google Drive
def subir_a_drive(ruta_local, nombre_drive):
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    creds = credentials
    service = build("drive", "v3", credentials=creds)
    archivo = MediaFileUpload(ruta_local, resumable=True)
    respuesta = service.files().create(
        body={
            "name": nombre_drive,
            "parents": ["1952GPiJ002KyA8hYkEnt7nvSSGAHweoN"],  # ID carpeta destino
        },
        media_body=archivo,
        fields="id"
    ).execute()
    file_id = respuesta.get("id")
    return f"https://drive.google.com/file/d/{file_id}/view?usp=sharing"

# Generar video
def generar_video(idea, imagenes):
    clips = []
    duracion_total = 12
    duracion_por_imagen = duracion_total / len(imagenes)

    for url in imagenes:
        img = ImageClip(url).set_duration(duracion_por_imagen).resize(height=1080).set_position("center")
        clips.append(img)

    video = concatenate_videoclips(clips, method="compose")

    audio = AudioFileClip("assets/musica.mp3").subclip(0, duracion_total)
    video = video.set_audio(audio)

    nombre_archivo = f"video_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.mp4"
    ruta_salida = f"/tmp/{nombre_archivo}"
    video.write_videofile(ruta_salida, fps=30, codec="libx264", audio_codec="aac")

    return ruta_salida, nombre_archivo

@app.route("/", methods=["GET"])
def home():
    return "Servidor en producción con Gunicorn ✅"

@app.route("/generar_video", methods=["POST"])
def generar():
    data = request.get_json()
    idea = data.get("idea")
    imagenes = data.get("imagenes")

    if not idea or not imagenes:
        return jsonify({"error": "Faltan campos 'idea' o 'imagenes'"}), 400

    try:
        ruta_video, nombre_video = generar_video(idea, imagenes)
        video_url = subir_a_drive(ruta_video, nombre_video)
        return jsonify({"status": "ok", "video_url": video_url})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)




