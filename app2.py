import pytesseract
from PIL import Image
import pdfplumber
import os

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def extract_text(file_path):
    text = ""

    if file_path.endswith(".pdf"):
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"

    else:  # image files
        image = Image.open(file_path)
        text = pytesseract.image_to_string(image)

    return text

from flask import Flask, render_template, request
from openai import OpenAI

app = Flask(__name__)
client = OpenAI()

SYSTEM_PROMPT = """
You are an AI Tutor for secondary school students.
Explain concepts clearly and simply.
Be encouraging and supportive.
Do not provide exam cheating answers.
"""

chat_history = [
    {"role": "system", "content": SYSTEM_PROMPT}
]

@app.route("/", methods=["GET", "POST"])
def index():
    tutor_reply = ""

    if request.method == "POST":
        user_input = request.form["question"]

        chat_history.append({"role": "user", "content": user_input})

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=chat_history
        )

        tutor_reply = response.choices[0].message.content
        chat_history.append({"role": "assistant", "content": tutor_reply})

    return render_template("index.html", reply=tutor_reply)

if __name__ == "__main__":
    app.run(debug=True)





