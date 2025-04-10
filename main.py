import os
from openai import OpenAI
from PyPDF2 import PdfReader
from diffusers import AutoencoderKLWan, WanPipeline
from diffusers.utils import export_to_video
import torch
from flask import Flask, request, jsonify, render_template, redirect, url_for
from gtts import gTTS
import mysql.connector
from db_config import DB_CONFIG
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

client = OpenAI(
    api_key="sk-0dcf4b20d5b0499c81cb99b382235dca", #generate summary API
    base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def get_connection():
    return mysql.connector.connect(**DB_CONFIG)

# === ROUTES ===

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        try:
            conn = get_connection()
            print("Connected to database")
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
            user = cursor.fetchone()
            print("User:", user)
            cursor.close()
            conn.close()

            if user:
                return redirect(url_for('upload_page'))
            else:
                return render_template('loginpage.html', error="Invalid credentials")
        except mysql.connector.Error as err:
            print("Login Error:", err)
            return render_template('loginpage.html', error="Database error. Try again.")

    return render_template('loginpage.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        try:
            conn = get_connection()
            cursor = conn.cursor()
            print("Connected to database")

            # Check for duplicate username or email
            cursor.execute("SELECT DATABASE();")
            print("Connected DB:", cursor.fetchone())
            cursor.execute("SHOW TABLES;")
            print("Tables:", cursor.fetchall())

            cursor.execute("SELECT * FROM users WHERE username = %s OR email = %s", (username, email))
            existing_user = cursor.fetchone()

            if existing_user:
                error_msg = "Username or email already exists."
                return render_template('registerpage.html', error=error_msg)

            # Insert new user
            cursor.execute(
                "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                (username, email, password)
            )
            conn.commit()
            cursor.close()
            conn.close()
            return redirect(url_for('login'))

        except mysql.connector.Error as err:
            print("Registration Error:", err)
            return render_template('registerpage.html', error="Database error. Please try again.")

    return render_template('registerpage.html')


@app.route('/uploadpage')
def upload_page():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files.get('document')
    if not file:
        return jsonify({"error": "No file uploaded."}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)  # ✅ Save the uploaded file

    # Extract text from saved PDF
    reader = PdfReader(file_path)
    all_text = ""
    for page in reader.pages:
        text = page.extract_text()
        if text:
            all_text += text + "\n"

    summary = summaryfunction(all_text)
    script = audiofunction(all_text)
    scene_and_summary = videofunction(all_text)
    print("Scene and Summary:", scene_and_summary)
    print("Summary:", summary)
    print("Script:", script)
    generateaudio(script)
    #generatevideo(scene_and_summary)
    #generatecomic(scene_and_summary)

    return jsonify({
        "summary": summary,
        "filename": filename,
        "status": "Video and audio generated successfully."
    })


# === FUNCTIONS ===
def videofunction(text):
    try:
        client2 = OpenAI(
        api_key="sk-ca96cedce775437a864a0d4f26fce184", #generate scenes and summary API
        base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
        )
        completion2 = client2.chat.completions.create(
            model="qwen-plus",
            messages=[
                {'role': 'system', 'content': 'You are a helpful assistant.'},
                {'role': 'user', 'content': 'Give me scenes for a video regarding: ' + text}
            ]
        )
        return completion2.choices[0].message.content
    except Exception as e:
        return f"Error during scene generation: {e}"

def summaryfunction(text): #generate summary
    try:
        completion = client.chat.completions.create(
            model="qwen-plus",
            messages=[
                {'role': 'system', 'content': 'You are a helpful assistant.'},
                {'role': 'user', 'content': 'Give me a summary regarding: ' + text}
            ]
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error during summarization: {e}"

def audiofunction(text):
    try:
        completion = client.chat.completions.create(
            model="qwen-plus",
            messages=[
                {'role': 'system', 'content': 'You are a helpful assistant.'},
                {'role': 'user', 'content': 'Give me a script regarding: ' + text + ' (pure words, no character names or motion)'}
            ]
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error during script generation: {e}"

def generateaudio(text):
    try:
        tts = gTTS(text)
        tts.save("static/output.mp3")
    except Exception as e:
        print(f"Audio generation error: {e}")

def generatevideo(text):
    pass

def generatecomic(text):
    pass

if __name__ == '__main__':
    app.run(debug=True)
