import streamlit as st
import openai
import os
import pytesseract
from PIL import Image
import pdfplumber

# ---------------------------
# CONFIG
# ---------------------------
openai.api_key = os.getenv("OPENAI_API_KEY")

st.set_page_config(
    page_title="AI Tutor Bot",
    layout="wide"
)

st.title("📘 AI Tutor Bot")
st.caption("Upload notes • Chat with AI • Revise smarter")

# ---------------------------
# SESSION STATE
# ---------------------------
if "notes_text" not in st.session_state:
    st.session_state.notes_text = ""

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ---------------------------
# LAYOUT
# ---------------------------
col1, col2, col3 = st.columns([1, 2, 1])

# ---------------------------
# CENTER: UPLOAD
# ---------------------------
with col2:
    st.subheader("📤 Upload Study Notes")

    uploaded_file = st.file_uploader(
        "Upload PDF or image",
        type=["pdf", "png", "jpg", "jpeg"]
    )

    if uploaded_file:
        with st.spinner("Extracting text..."):
            extracted_text = ""

            if uploaded_file.type == "application/pdf":
                with pdfplumber.open(uploaded_file) as pdf:
                    for page in pdf.pages:
                        text = page.extract_text()
                        if text:
                            extracted_text += text + "\n"
            else:
                image = Image.open(uploaded_file)
                extracted_text = pytesseract.image_to_string(image)

            st.session_state.notes_text = extracted_text.strip()

        if st.session_state.notes_text:
            st.success("✅ Text extracted successfully!")
        else:
            st.warning("⚠️ No text detected.")

    st.markdown("---")
    st.markdown("### 📝 How to use")
    st.markdown("""
    1. Upload your study notes  
    2. Wait for text extraction  
    3. Ask questions in the chat  
    4. Request summaries, quizzes, or flashcards  
    """)

# ---------------------------
# RIGHT: CHAT
# ---------------------------
with col3:
    st.subheader("💬 AI Tutor Chat")

    for role, message in st.session_state.chat_history:
        if role == "user":
            st.chat_message("user").write(message)
        else:
            st.chat_message("assistant").write(message)

    user_input = st.chat_input("Ask your tutor...")

    if user_input:
        st.session_state.chat_history.append(("user", user_input))

        if not st.session_state.notes_text:
            reply = "📂 Please upload notes first so I can help you."
        else:
            prompt = f"""
You are an AI tutor.
Use the following study notes to answer the student's question.

STUDY NOTES:
{st.session_state.notes_text}

QUESTION:
{user_input}
"""

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}]
            )

            reply = response.choices[0].message.content.strip()

        st.session_state.chat_history.append(("assistant", reply))
        st.chat_message("assistant").write(reply)
