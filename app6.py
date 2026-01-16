import streamlit as st
import streamlit.components.v1 as components
import pytesseract
from PIL import Image
import pdfplumber
import os
from openai import OpenAI


# ----------------------------------
# CONFIG
# ----------------------------------
st.set_page_config(page_title="TutorBot", layout="centered")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ----------------------------------
# FUNCTIONS
# ----------------------------------

def extract_text(file):
    text = ""

    if file.type == "application/pdf":
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"

    else:  # Image files
        image = Image.open(file)
        text = pytesseract.image_to_string(image)

    return text.strip()


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

def show_flashcards(raw_text):
    cards = []

    for line in raw_text.split("\n"):
        if "-" in line:
            q, a = line.split("-", 1)
            cards.append((q.strip(), a.strip()))
                
# Generate HTML for flip cards
    html = """
    <style>
    .container {
        display: flex;
        flex-wrap: wrap;
        gap: 15px;
    }
    .card {
        width: 220px;
        height: 140px;
        perspective: 1000px;
    }
    .inner {
        position: relative;
        width: 100%;
        height: 100%;
        transition: transform 0.6s;
        transform-style: preserve-3d;
        cursor: pointer;
    }
    .card:hover .inner {
        transform: rotateY(180deg);
    }
    .front, .back {
        position: absolute;
        width: 100%;
        height: 100%;
        backface-visibility: hidden;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 10px;
        font-size: 15px;
        text-align: center;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    .front {
        background: #4CAF50;
        color: white;
    }
    .back {
        background: #ffffff;
        color: black;
        transform: rotateY(180deg);
        border: 1px solid #ccc;
    }
    </style>
    <div class="container">
    """

    for q, a in cards:
        html += f"""
        <div class="card">
            <div class="inner">
                <div class="front">{q}</div>
                <div class="back">{a}</div>
            </div>
        </div>
        """

    html += "</div>"

    components.html(html, height=450, scrolling=True)



    
# ----------------------------------
# UI
# ----------------------------------

st.title("📘 AI Study Assistant")
st.caption("Upload notes → Extract text → Learn smarter")

uploaded_file = st.file_uploader(
    "Upload PDF or Image",
    type=["pdf", "png", "jpg", "jpeg"]
)

action = st.radio(
    "Choose an action:",
    ["Summarize Notes", "Generate Quiz", "Create Flashcards"]
)

if uploaded_file:
    with st.spinner("Extracting text..."):
        extracted_text = extract_text(uploaded_file)

    if extracted_text:
        st.success("✅ Text extracted successfully")

        #with st.expander("📄 View Extracted Text"):
        #    st.text_area("", extracted_text, height=250)

        if st.button("🚀 Generate Output"):

            with st.spinner("Processing..."):

                if action == "Summarize Notes":
                    result = summarize_notes(extracted_text)
                    st.subheader("📌 Summary")
                    st.text_area("", result, height=300)

                elif action == "Generate Quiz":
                    result = generate_quiz(extracted_text)
                    st.subheader("📝 Quiz")
                    st.text_area("", result, height=300)

                elif action == "Create Flashcards":
                    result = generate_flashcards(extracted_text)
                    st.subheader("🧠 Flashcards")
                    show_flashcards(result)

    else:
        st.warning("⚠️ No text detected. Try a clearer file.")

# ----------------------------------
# FOOTER
# ----------------------------------
st.markdown("---")
st.markdown("🔒 **Note:** OCR works best in local environment.")
