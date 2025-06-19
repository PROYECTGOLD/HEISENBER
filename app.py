from flask import Flask, request, jsonify
from moviepy.editor import *
import os
import datetime
import tempfile
import uuid
import shutil
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from PIL import Image
import requests
from io import BytesIO

app = Flask(__name__)

# Rutas
GOOGLE_CREDENTIALS_PATH = "/etc/secrets/heisenberg-credentials.json"
FOLDER_ID = "1952GPiJ002KyA8hYkEnt7nvSSGAHweoN"  # Tu carpeta de destino en Drive
SHEET_ID = "1lcGzXs4QR2rjvVJR8E8Eo8znLZbMALYpnF4AZgn5BMQ"
SHEET_NAME = "ideas"

def crear_video(idea, imagenes_urls, output_path):
    clips = []

    # Duración por imagen (3 imágenes en 12 segundos)
    duracion_por_imagen = 12 / len(imagenes_urls)

    for url in imagenes_urls:
        response = requests.get(url)
        image = Image.open(BytesIO(response.content)).convert("RGB")
        temp_img = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
        image.save(temp_img.name)
        img_clip = ImageClip(temp_img.name).set_duration(duracion_por_imagen).resize(height=1080).set_position("center")
        clips.append(img_clip)

    final_clip = concatenate_videoclips(clips, method="compose")

    # Música de fondo
    audio = AudioFileClip("assets/musica.mp3").set_duration(final_clip.duration)
    final_clip = final_clip.set_audio(audio)

    final_clip.write_videofile(output_path, fps=24)
    for clip in clips:
        os.unlink(clip.filename)

def subir_a_drive(local_path, filename):
    from pydrive.auth import GoogleAuth
    from pydrive.drive import GoogleDrive

    gauth = GoogleAuth()
    gauth.LoadCredentialsFile(GOOGLE_CREDENTIALS_PATH)
    if gauth.credentials is None:
        gauth.LocalWebserverAuth()
    else:
        gauth.Authorize()
    gauth.SaveCredentialsFile(GOOGLE_CREDENTIALS_PATH)

    drive = GoogleDrive(gauth)
    file_drive = drive.CreateFile({'title': filename, 'parents': [{"id": FOLDER_ID}]})
    file_drive.SetContentFile(local_path)
    file_drive.Upload()
    return file_drive['alternateLink']

def marcar_como_hecho(fila):
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_CREDENTIALS_PATH, scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)
    cell = sheet.find(fila['idea'])
    if cell:
        sheet.update_cell(cell.row, 4, "hecho")

@app.route('/generar_video', methods=['POST'])
def generar_video():
    data = request.get_json()
    idea = data.get("idea")
    imagenes = data.get("imagenes")

    if not idea or not imagenes or len(imagenes) < 3:
        return jsonify({"error": "Faltan datos necesarios (idea o imágenes)"}), 400

    output_name = f"video_{uuid.uuid4().hex[:8]}.mp4"
    output_path = os.path.join(tempfile.gettempdir(), output_name)

    try:
        crear_video(idea, imagenes[:3], output_path)
        video_url = subir_a_drive(output_path, output_name)
        marcar_como_hecho({"idea": idea})
        return jsonify({"video_url": video_url}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if os.path.exists(output_path):
            os.remove(output_path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)





