from flask import Flask, request, jsonify
from moviepy.editor import *
from datetime import datetime
import requests
import os
import random
import string
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from pydub import AudioSegment
from pydub.playback import play

# Config
CARPETA_DRIVE_ID = '1952GPiJ002KyA8hYkEnt7nvSSGAHweoN'
CREDENTIALS_PATH = '/etc/secrets/heisenberg-credentials.json'
SPREADSHEET_ID = '1lcGzXs4QR2rjvVJR8E8Eo8znLZbMALYpnF4AZgn5BMQ'

app = Flask(__name__)

def generar_nombre():
    return 'video_' + datetime.now().strftime('%Y%m%d%H%M%S') + '.mp4'

def generar_imagenes(idea):
    imagenes = []
    for i in range(3):
        url = 'https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2'
        headers = {"Authorization": f"Bearer {os.getenv('HF_TOKEN')}"}
        payload = {"inputs": idea}
        response = requests.post(url, headers=headers, json=payload)
        filename = f"imagen_{i}.jpg"
        with open(filename, "wb") as f:
            f.write(response.content)
        imagenes.append(filename)
    return imagenes

def generar_musica():
    musica = random.choice(['musica1.mp3', 'musica2.mp3', 'musica3.mp3'])
    return AudioFileClip(musica).subclip(0, 12)

def generar_video(imagenes):
    clips = []
    duracion = 4
    for img in imagenes:
        clips.append(ImageClip(img).set_duration(duracion).resize(height=1080).set_position("center"))
    video = concatenate_videoclips(clips, method="compose")
    return video

def subir_a_drive(nombre_video):
    from pydrive.auth import GoogleAuth
    from pydrive.drive import GoogleDrive
    
    gauth = GoogleAuth()
    gauth.LoadCredentialsFile(CREDENTIALS_PATH)
    gauth.LocalWebserverAuth()
    drive = GoogleDrive(gauth)

    file = drive.CreateFile({'title': nombre_video, 'parents': [{'id': CARPETA_DRIVE_ID}]})
    file.SetContentFile(nombre_video)
    file.Upload()
    return file['alternateLink']

def actualizar_hoja(fila, video_url):
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_PATH, scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SPREADSHEET_ID).sheet1
    sheet.update_cell(fila, 4, video_url)
    sheet.update_cell(fila, 3, 'hecho')

@app.route('/generar_video', methods=['POST'])
def generar_video_endpoint():
    data = request.get_json()
    idea = data.get("idea")
    texto = data.get("text")
    fila = data.get("fila")  # número de fila a actualizar

    try:
        imagenes = generar_imagenes(idea)
        video_clip = generar_video(imagenes)
        audio_clip = generar_musica()

        final = video_clip.set_audio(audio_clip)
        nombre_video = generar_nombre()
        final.write_videofile(nombre_video, fps=24)

        video_url = subir_a_drive(nombre_video)
        actualizar_hoja(fila, video_url)

        return jsonify({"video_url": video_url})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)







