import os
from google.cloud import texttospeech
from flask import Flask, request, render_template, redirect, flash
from dotenv import load_dotenv
from pdfminer.high_level import extract_text
from werkzeug.utils import secure_filename


load_dotenv()
port = os.getenv('PORT')
app = Flask(__name__)
ALLOWED_EXTENSIONS = ['pdf', 'txt', 'docx', 'rtf']
app.secret_key = os.getenv('SECRET_KEY')

client_id = os.getenv('GOOGLE_AUTH')

client = texttospeech.TextToSpeechClient(credentials=client_id)


@app.route("/", methods=['GET'])
def home():
    if request.method == 'GET':
        return render_template('index.html')


@app.route("/uploader", methods=["POST"])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
        else:
            file = request.files['file']
            extension = file.filename.split(".")[-1]
            if extension in ALLOWED_EXTENSIONS:
                filename = secure_filename(file.filename)
                filepath = os.path.join(os.getenv('UPLOAD_FOLDER'), filename)
                file.save(filepath)
                match extension:
                    case 'pdf':
                        text = extract_text(filepath)
                        print(text)
                        os.remove(filepath)

        return redirect("/")

if __name__ == '__main__':
    app.run(port=port, debug=True)
