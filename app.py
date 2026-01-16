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
            

def tutor_chat(user_message, context_text=""):
    system_prompt = f"""
    You are a friendly AI tutor.
    Explain clearly, step-by-step, using simple language.
    Use the following study notes as context if relevant:

    {context_text}
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        max_tokens=300
    )

    return response.choices[0].message.content

# -----------------------------
# SESSION STATE
# -----------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


# ----------------------------------
# UI
# ----------------------------------

st.title("📘 Tutorbot")
col1, col2 = st.columns([4, 4])
    
with col1:
    

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
              #  st.text_area("", extracted_text, height=200)

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
                        st.caption("Hover over a card to reveal the answer")
                        show_flashcards(result)


with col2:
    st.subheader("💬 AI Tutor Chat")

    st.caption("Ask questions about your uploaded notes")

    # Display chat history
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat input box
    user_input = st.chat_input("Ask your tutor...")

    if user_input:
        # Show user message
        st.session_state.chat_history.append(
            {"role": "user", "content": user_input}
        )

        with st.chat_message("user"):
            st.markdown(user_input)

        with st.spinner("Tutor is thinking..."):
            reply = tutor_chat(
                user_input,
                context_text=extracted_text if uploaded_file else ""
            )

        # Show tutor reply
        st.session_state.chat_history.append(
            {"role": "assistant", "content": reply}
        )

        with st.chat_message("assistant"):
            st.markdown(reply)



# ----------------------------------
# FOOTER
# ----------------------------------
st.markdown("---")
st.markdown("🔒 **Note:** OCR works best in local environment.")
