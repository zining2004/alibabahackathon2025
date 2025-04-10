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

app = Flask(__name__)

client = OpenAI(
    api_key="sk-0dcf4b20d5b0499c81cb99b382235dca",
    base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
)

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

            # Check for duplicate username or email
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

    reader = PdfReader(file)
    all_text = ""
    for page in reader.pages:
        text = page.extract_text()
        if text:
            all_text += text + "\n"

    summary = summaryfunction(all_text)
    script = audiofunction(all_text)
    generateaudio(script)
    generatevideo(summary)

    return jsonify({
        "summary": summary,
        "status": "Video and audio generated successfully."
    })


# === FUNCTIONS ===

def summaryfunction(text):
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
    try:
        model_id = "Wan-AI/Wan2.1-T2V-14B-Diffusers"
        vae = AutoencoderKLWan.from_pretrained(model_id, subfolder="vae", torch_dtype=torch.float32)
        pipe = WanPipeline.from_pretrained(model_id, vae=vae, torch_dtype=torch.bfloat16)
        pipe.to("cuda")

        output = pipe(
            prompt=text,
            negative_prompt="low quality, bad anatomy, poorly drawn, static",
            height=480,
            width=832,
            num_frames=81,
            guidance_scale=5.0
        ).frames[0]

        export_to_video(output, "static/output.mp4", fps=15)
    except Exception as e:
        print(f"Video generation error: {e}")


if __name__ == '__main__':
    app.run(debug=True)
