import os
import random
from flask import Flask, request, jsonify
from moviepy.editor import *
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# Cargar credenciales de Google
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
credentials_path = '/etc/secrets/heisenberg-463407-63df8f900747.json'
creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_path, scope)
client = gspread.authorize(creds)

# Google Sheets
spreadsheet_id = '1lcGzXs4QR2rjvVJR8E8Eo8znLZbMALYpnF4AZgn5BMQ'
sheet = client.open_by_key(spreadsheet_id).sheet1

# Drive
folder_id = '1952GPiJ002KyA8hYkEnt7nvSSGAHweoN'

app = Flask(__name__)

@app.route('/generar_video', methods=['POST'])
def generar_video():
    data = request.get_json()
    idea = data.get("idea", "Sin título")
    text = data.get("text", "")

    # 1. Generar 3 imágenes simuladas (aquí puedes usar Replicate o similar)
    clips = []
    for i in range(3):
        img = ColorClip(size=(720, 1280), color=random_color(), duration=4)
        txt = TextClip(idea, fontsize=60, color='white', size=img.size, method='caption')
        txt = txt.set_position('center').set_duration(4)
        final = CompositeVideoClip([img, txt])
        clips.append(final)

    video = concatenate_videoclips(clips)
    audio = AudioFileClip("assets/musica.mp3").subclip(0, 12)
    video = video.set_audio(audio)

    nombre_archivo = f"video_{datetime.now().strftime('%Y%m%d%H%M%S')}.mp4"
    ruta_video = f"/tmp/{nombre_archivo}"
    video.write_videofile(ruta_video, fps=24)

    # 2. Subir a Google Drive
    from pydrive.auth import GoogleAuth
    from pydrive.drive import GoogleDrive
    gauth = GoogleAuth()
    gauth.credentials = creds
    drive = GoogleDrive(gauth)

    upload_file = drive.CreateFile({'title': nombre_archivo, 'parents': [{"id": folder_id}]})
    upload_file.SetContentFile(ruta_video)
    upload_file.Upload()
    video_url = f"https://drive.google.com/file/d/{upload_file['id']}/view"

    # 3. Marcar como "hecho"
    celda = buscar_fila_por_idea(sheet, idea)
    if celda:
        sheet.update_cell(celda.row, celda.col + 2, "hecho")
        sheet.update_cell(celda.row, celda.col + 3, video_url)

    return jsonify({"status": "ok", "video_url": video_url})

def buscar_fila_por_idea(sheet, idea):
    celdas = sheet.findall(idea)
    return celdas[0] if celdas else None

def random_color():
    return tuple(random.randint(0, 255) for _ in range(3))

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=10000)





