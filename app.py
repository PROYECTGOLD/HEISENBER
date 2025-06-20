from flask import Flask, request, jsonify
from moviepy.editor import ImageClip, concatenate_videoclips, AudioFileClip
import os
import tempfile

app = Flask(__name__)

@app.route("/generar_video", methods=["POST"])
def generar_video():
    data = request.get_json()
    idea = data.get("idea")
    imagenes = data.get("imagenes", [])

    if not idea or not imagenes:
        return jsonify({"error": "Faltan datos"}), 400

    clips = []
    for img_url in imagenes:
        clip = ImageClip(img_url).set_duration(4).resize(height=1080).set_position("center")
        clips.append(clip)

    final = concatenate_videoclips(clips, method="compose")

    # Música de fondo opcional
    # audio = AudioFileClip("music.mp3")
    # final = final.set_audio(audio)

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    final.write_videofile(temp_file.name, fps=24)

    video_url = f"https://drive.google.com/fake_url/{os.path.basename(temp_file.name)}"

    return jsonify({"video_url": video_url})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)








