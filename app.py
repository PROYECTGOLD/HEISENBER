from flask import Flask, request, jsonify
from moviepy.editor import ImageClip, concatenate_videoclips, AudioFileClip
from datetime import datetime
import os
import requests
import tempfile
import shutil
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)

# Cargar credenciales desde ruta segura en Render
CREDENTIALS_PATH = "/etc/secrets/heisenberg-credentials.json"

# Ruta de la carpeta de destino en Google Drive
FOLDER_ID = "1952GPiJ002KyA8hYkEnt7nvSSGAHweoN"

def upload_to_drive(file_path, file_name):
    scope = ['https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_PATH, scope)
    gauth = GoogleAuth()
    gauth.credentials = credentials
    drive = GoogleDrive(gauth)

    file_drive = drive.CreateFile({'title': file_name, 'parents': [{'id': FOLDER_ID}]})
    file_drive.SetContentFile(file_path)
    file_drive.Upload()
    return file_drive['alternateLink']

@app.route("/generar_video", methods=["POST"])
def generar_video():
    try:
        data = request.get_json()

        # Validaciones básicas
        if not data:
            return jsonify({"error": "Falta cuerpo JSON"}), 400

        idea = data.get("idea")
        imagenes = data.get("imagenes")

        if not idea or not imagenes or len(imagenes) != 3:
            return jsonify({"error": "Faltan campos: idea o 3 imágenes"}), 400

        # Crear clips
        temp_dir = tempfile.mkdtemp()
        clips = []

        for idx, url in enumerate(imagenes):
            try:
                response = requests.get(url, stream=True)
                if response.status_code != 200:
                    return jsonify({"error": f"Imagen {idx+1} no descargada correctamente"}), 400
                img_path = os.path.join(temp_dir, f"img{idx}.jpg")
                with open(img_path, 'wb') as f:
                    f.write(response.content)
                clip = ImageClip(img_path, duration=4).resize(height=1920).resize(width=1080)
                clips.append(clip)
            except Exception as e:
                return jsonify({"error": f"Error con imagen {idx+1}: {str(e)}"}), 400

        # Música de fondo opcional
        audio = AudioFileClip("assets/music.mp3").volumex(0.5)
        final_video = concatenate_videoclips(clips, method="compose")
        final_video = final_video.set_audio(audio).set_duration(12)

        output_path = os.path.join(temp_dir, "output.mp4")
        final_video.write_videofile(output_path, fps=24)

        # Subir a Drive
        nombre_archivo = f"video_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
        video_url = upload_to_drive(output_path, nombre_archivo)

        shutil.rmtree(temp_dir)
        return jsonify({"video_url": video_url})

    except Exception as e:
        return jsonify({"error": "Error interno del servidor", "detalle": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=10000)






