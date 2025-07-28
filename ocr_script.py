from google.cloud import vision
import io

# هنا اسم الملف اللي حملته من Google Cloud
client = vision.ImageAnnotatorClient.from_service_account_file("my-project-key-01a2b3c4.json")

# هنا اسم الصورة اللي عايز تعملها OCR (لازم تكون في نفس الفولدر أو تكتب المسار كامل)
with io.open("my-image.png", 'rb') as image_file:
    content = image_file.read()

image = vision.Image(content=content)

# اعمل OCR
response = client.text_detection(image=image)
texts = response.text_annotations

# اطبع النصوص
for text in texts:
    print(text.description)
