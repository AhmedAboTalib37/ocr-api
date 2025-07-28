from flask import Flask, request, jsonify
import os
from google.cloud import vision
from werkzeug.utils import secure_filename
import threading

app = Flask(__name__)

# Set your credentials JSON
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "my-project-key-01a2b3c4.json"

# إنشاء client مرة واحدة علشان نستخدمه في كل الـ requests
vision_client = vision.ImageAnnotatorClient()

lock = threading.Lock()

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['image']
    filename = secure_filename(file.filename)
    filepath = os.path.join("uploads", filename)
    file.save(filepath)

    # OCR using Google Vision
    with open(filepath, "rb") as image_file:
        content = image_file.read()

    image = vision.Image(content=content)

    # نستخدم lock علشان نضمن سلامة الـ Thread لما يستخدم نفس الـ client
    with lock:
        response = vision_client.text_detection(image=image)

    texts = response.text_annotations

    # حذف الصورة بعد التحليل لتقليل الضغط
    os.remove(filepath)

    if texts:
        return jsonify({"text": texts[0].description})
    else:
        return jsonify({"text": "لم يتم العثور على نص"})

if __name__ == '__main__':
    if not os.path.exists("uploads"):
        os.makedirs("uploads")

    # نشغلها على Gunicorn في البيئة الحقيقية، لكن مؤقتًا للتجريب:
    app.run(host="0.0.0.0", port=5000, threaded=True)
