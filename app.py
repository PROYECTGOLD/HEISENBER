from flask import Flask, request, jsonify
from moviepy.editor import ImageClip, concatenate_videoclips
import tempfile
import os

app = Flask(__name__)

@app.route("/generar_video", methods=["POST"])
def generar_video():
    try:
        data = request.get_json()
        idea = data.get("idea")
        imagenes = data.get("imagenes", [])

        if not idea or not imagenes:
            return jsonify({"error": "Faltan datos"}), 400

        clips = []
        for img_url in imagenes:
            clips.append(ImageClip(img_url).set_duration(4).resize(height=1080).set_position("center"))

        final_clip = concatenate_videoclips(clips, method="compose")
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
        output_path = temp_file.name
        final_clip.write_videofile(output_path, fps=24)

        # (Aquí pondrías lógica para subir a Drive)

        return jsonify({"video_url": f"https://fakeurl.com/{os.path.basename(output_path)}"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)









