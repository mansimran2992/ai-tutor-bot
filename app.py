#OCR Function
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

#summarize notes

def summarize_notes(text):
    prompt = f"""
    Summarize the following notes in simple bullet points
    suitable for school students:

    {text}
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content

#Generate Quiz Questions

def generate_quiz(text):
    prompt = f"""
    Create 5 quiz questions with answers based on these notes:

    {text}
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content

#Create Flashcards

def generate_flashcards(text):
    prompt = f"""
    Create flashcards from these notes.
    Format as:
    Question - Answer

    {text}
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content

#Flask Route (Main Logic)

from flask import Flask, render_template, request
from openai import OpenAI

app = Flask(__name__)
client = OpenAI()

@app.route("/", methods=["GET", "POST"])
def index():
    result = ""

    if request.method == "POST":
        file = request.files["file"]
        action = request.form["action"]

        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)

        extracted_text = extract_text(file_path)

        if action == "summary":
            result = summarize_notes(extracted_text)
        elif action == "quiz":
            result = generate_quiz(extracted_text)
        elif action == "flashcards":
            result = generate_flashcards(extracted_text)

    return render_template("index.html", result=result)

if __name__ == "__main__":
    app.run(debug=True)


chat_history = [
    {
        "role": "system",
        "content": "You are a friendly AI tutor. Explain clearly and encourage learning."
    }
]

@app.route("/chat", methods=["GET", "POST"])
def chat():
    if request.method == "POST":
        user_message = request.form["message"]

        chat_history.append({"role": "user", "content": user_message})

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=chat_history,
            max_tokens=250
        )

        tutor_reply = response.choices[0].message.content
        chat_history.append({"role": "assistant", "content": tutor_reply})

    return render_template("chat.html", chat_history=chat_history)


#@app.route("/flashcards")
#def flashcards():
#    raw_cards = session.get("flashcard_text", "")
#    cards = []

#    for line in raw_cards.split("\n"):
#        if "|" in line:
#            q, a = line.split("|", 1)
#            cards.append({"question": q, "answer": a})

#    return render_template("flashcards.html", flashcards=cards)

