from flask import Flask, request, jsonify
app = Flask(__name__)

@app.route("/")
def home():
    return "Servidor activo ✅"

@app.route("/generar_video", methods=["POST"])
def generar_video():
    return jsonify({"status": "ok", "video_url": "https://example.com/video.mp4"})
