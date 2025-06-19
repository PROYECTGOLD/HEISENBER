from flask import Flask, request, jsonify
from moviepy.editor import TextClip, CompositeVideoClip
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import os
import uuid


SERVICE_ACCOUNT_FILE = 'service_account.json'
SCOPES = ['https://www.googleapis.com/auth/drive']

def get_drive_service():
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return build('drive', 'v3', credentials=credentials)

def generar_video(texto, nombre_archivo):
    clip = TextClip(texto, fontsize=70, color='white', size=(720, 1280))
    clip = clip.set_duration(5)
    video = CompositeVideoClip([clip])
    video.write_videofile(nombre_archivo, fps=24)

def subir_a_drive(nombre_archivo):
    service = get_drive_service()
    file_metadata = {
        'name': nombre_archivo,
        'parents': ['1d7HqxZpTgKoR0h9ZBxkEpPf4YO0EjR5a']
    }
    media = MediaFileUpload(nombre_archivo, mimetype='video/mp4')
    archivo = service.files().create(body=file_metadata, media_body=media, fields='id').execute()

    file_id = archivo.get('id')
    service.permissions().create(
        fileId=file_id,
        body={'role': 'reader', 'type': 'anyone'},
    ).execute()

    enlace = f"https://drive.google.com/uc?id={file_id}&export=download"
    return enlace

@app.route("/")
def home():
    return "Servidor listo y conectado a tu carpeta personal ✅"

@app.route("/generar_video", methods=["POST"])
def generar():
    data = request.get_json()
    idea = data.get("idea", "sin_idea")
    texto = data.get("text", "sin_texto")

    nombre_archivo = f"{uuid.uuid4().hex}_{idea.replace(' ', '_')}.mp4"
    generar_video(texto, nombre_archivo)
    enlace_drive = subir_a_drive(nombre_archivo)
    os.remove(nombre_archivo)

    return jsonify({
        "status": "ok",
        "video_url": enlace_drive
    })