from flask import Flask, request, jsonify
import os
from google.cloud import vision
from werkzeug.utils import secure_filename
import threading

app = Flask(__name__)

# تحديد مسار ملف الكريدنشلز (سواء محليًا أو من /etc/secrets)
CREDENTIAL_PATH = "my-project-key-01a2b3c4.json"
if os.path.exists("/etc/secrets/" + CREDENTIAL_PATH):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = f"/etc/secrets/{CREDENTIAL_PATH}"
else:
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = CREDENTIAL_PATH

# إنشاء عميل Google Vision مرة واحدة
vision_client = vision.ImageAnnotatorClient()

# لوك لتأمين الـ Thread عند استخدام الـ client
lock = threading.Lock()

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['image']
    filename = secure_filename(file.filename)
    filepath = os.path.join("uploads", filename)
    file.save(filepath)

    with open(filepath, "rb") as image_file:
        content = image_file.read()

    image = vision.Image(content=content)

    with lock:
        response = vision_client.text_detection(image=image)

    texts = response.text_annotations

    os.remove(filepath)

    if texts:
        return jsonify({"text": texts[0].description})
    else:
        return jsonify({"text": "لم يتم العثور على نص"})

if __name__ == '__main__':
    if not os.path.exists("uploads"):
        os.makedirs("uploads")

    app.run(host="0.0.0.0", port=5000, threaded=True)
