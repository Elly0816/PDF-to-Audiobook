import os
from flask import Flask, request, render_template, redirect, flash, send_file
from dotenv import load_dotenv
from pdfminer.high_level import extract_text
from werkzeug.utils import secure_filename
import requests


load_dotenv()
port = os.getenv('PORT')
app = Flask(__name__)
ALLOWED_EXTENSIONS = ['pdf', 'txt', 'docx', 'rtf']
app.secret_key = os.getenv('SECRET_KEY')

api_key = os.getenv('API_KEY')
url = 'http://api.voicerss.org'
folder = os.getenv('UPLOAD_FOLDER')



@app.route("/", methods=['GET'])
def home():
    """Home route deletes all files in the uploads directory and then
    renders the index.html page"""
    if request.method == 'GET':
        with os.scandir(folder) as files:
            for file in files:
                os.remove(file)
        return render_template('index.html')

def convert(url, key, src, hl, c):
    """This handles the request to the api and returns a response object"""
    params = {
        'key': key,
        'src': src,
        'hl': hl,
        'c':c
    }
    response = requests.get(url, params=params)
    return response

@app.route("/uploader", methods=["POST"])
def upload_file():
    """This special route handles file uploads to the server"""
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
        else:
            file = request.files['file']
            extension = file.filename.split(".")[-1]
            download_name = file.filename.split(".")[0]
            if extension in ALLOWED_EXTENSIONS:
                filename = secure_filename(file.filename)
                filepath = os.path.join(folder, filename)
                file.save(filepath)
                match extension:
                    case 'pdf':
                        text = extract_text(filepath)
                        os.remove(filepath)
                        print(text)
                        data = convert(url, api_key, text, 'en-gb', 'mp3')
                        file_to_send = f'{folder}/{download_name}'
                        open(file_to_send, 'bx').write(data.content)
                        return send_file(f'{folder}/{download_name}',
                                         as_attachment=True,
                                         download_name=f'{download_name}.mp3')
        return redirect("/")


if __name__ == '__main__':
    app.run(port=port, debug=True)
