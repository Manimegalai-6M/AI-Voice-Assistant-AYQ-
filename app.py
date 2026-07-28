import os
from io import BytesIO
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv
from groq import Groq
from gtts import gTTS

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------

st.set_page_config(
    page_title="AYQ - AI Voice Assistant",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------
# CUSTOM CSS
# ---------------------------------------------------

st.markdown("""
<style>

html, body, [class*="css"]{
    background:#0F172A;
    color:white;
}

.main{
    background:#0F172A;
}

section[data-testid="stSidebar"]{
    background:#111827;
}

.hero{
    background:linear-gradient(90deg,#2563EB,#7C3AED);
    padding:35px;
    border-radius:20px;
    text-align:center;
    margin-bottom:20px;
    box-shadow:0px 10px 30px rgba(0,0,0,.35);
}

.hero h1{
    color:white;
    font-size:48px;
}

.hero p{
    color:#E5E7EB;
    font-size:20px;
}

.user-card{
    background:#1E293B;
    padding:18px;
    border-radius:15px;
    margin-top:15px;
    border-left:6px solid #3B82F6;
}

.ai-card{
    background:#162033;
    padding:18px;
    border-radius:15px;
    margin-top:15px;
    border-left:6px solid #8B5CF6;
}

.footer{
    margin-top:50px;
    text-align:center;
    color:#94A3B8;
    font-size:14px;
}

.stats{
    background:#111827;
    border-radius:15px;
    padding:18px;
    text-align:center;
}

hr{
    border:1px solid #374151;
}

</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# LOAD ENV
# ---------------------------------------------------

load_dotenv()

groq_api_key = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")

if not groq_api_key:
    st.error("GROQ_API_KEY not found.")
    st.stop()

client = Groq(api_key=groq_api_key)

# ---------------------------------------------------
# SESSION STATE
# ---------------------------------------------------

if "history" not in st.session_state:
    st.session_state.history=[]

if "questions" not in st.session_state:
    st.session_state.questions=0

# ---------------------------------------------------
# SIDEBAR
# ---------------------------------------------------

with st.sidebar:

    st.title("🤖 AUQ")

    st.write("Your Personal AI Assistant")

    st.divider()

    personality=st.selectbox(
        "AI Personality",
        [
            "General Assistant",
            "Teacher",
            "Programmer",
            "Motivator",
            "Interviewer"
        ]
    )

    language=st.selectbox(
        "Voice Language",
        [
            "English",
            "Tamil",
            "Hindi"
        ]
    )

    temperature=st.slider(
        "Creativity",
        0.0,
        1.0,
        0.3,
        0.1
    )

    st.divider()

    st.subheader("Statistics")

    st.metric(
        "Questions",
        st.session_state.questions
    )

    st.metric(
        "Conversation",
        len(st.session_state.history)
    )

    st.divider()

    if st.button("🗑 Clear Conversation"):

        st.session_state.history=[]

        st.session_state.questions=0

        st.rerun()

# ---------------------------------------------------
# HERO
# ---------------------------------------------------

st.markdown("""
<div class="hero">

<h1>🎙️ AYQ</h1>

<p>
Your Personal AI Voice Assistant
</p>

</div>
""",unsafe_allow_html=True)

# ---------------------------------------------------
# SYSTEM PROMPTS
# ---------------------------------------------------

SYSTEM_PROMPTS={

"General Assistant":
"You are a friendly AI assistant.",

"Teacher":
"Explain everything simply with examples.",

"Programmer":
"Answer like a senior software engineer. Include code whenever possible.",

"Motivator":
"Be encouraging and positive.",

"Interviewer":
"Behave like an interviewer and ask follow-up questions."

}

# ---------------------------------------------------
# FUNCTIONS
# ---------------------------------------------------

def generate_ai(question):

    response=client.chat.completions.create(

        model="llama-3.3-70b-versatile",

        messages=[
            {
                "role":"system",
                "content":SYSTEM_PROMPTS[personality]
            },
            {
                "role":"user",
                "content":question
            }
        ],

        temperature=temperature,

        max_tokens=400
    )

    return response.choices[0].message.content


def text_to_speech(text):

    audio=BytesIO()

    tts=gTTS(

        text=text,

        lang=language

    )

    tts.write_to_fp(audio)

    audio.seek(0)

    return audio


def speech_to_text(audio_bytes):

    transcript=client.audio.transcriptions.create(

        file=("audio.wav",audio_bytes),

        model="whisper-large-v3-turbo",

        response_format="json"

    )

    return transcript.text
# ---------------------------------------------------
# MAIN INTERFACE
# ---------------------------------------------------

st.subheader("🎤 Ask using your voice")

st.write(
    "Press the microphone below and record your question."
)

audio_value = st.audio_input("Record your question")

# ---------------------------------------------------
# PROCESS AUDIO
# ---------------------------------------------------

if audio_value is not None:

    audio_bytes = audio_value.getvalue()

    if len(audio_bytes) == 0:

        st.warning("No audio detected.")

        st.stop()

    st.audio(audio_value)

    # ---------------- Speech To Text ----------------

    with st.spinner("🎧 Listening..."):

        try:

            user_text = speech_to_text(audio_bytes)

        except Exception as e:

            st.error(f"Speech recognition failed.\n\n{e}")

            st.stop()

    if not user_text.strip():

        st.warning("No speech detected.")

        st.stop()

    # ---------------- Show User ----------------

    st.markdown(
        f"""
        <div class="user-card">

        <h4>👤 You</h4>

        <p>{user_text}</p>

        </div>
        """,
        unsafe_allow_html=True
    )

    # Save question count

    st.session_state.questions += 1

    # ---------------- AI Response ----------------

    with st.spinner("🧠 AUQ is thinking..."):

        ai_text = generate_ai(user_text)

    # ---------------- Show AI ----------------

    st.markdown(
        f"""
        <div class="ai-card">

        <h4>🤖 AYQ</h4>

        <p>{ai_text}</p>

        </div>
        """,
        unsafe_allow_html=True
    )

    # ---------------- Save Conversation ----------------

    st.session_state.history.append(
        {
            "time": datetime.now().strftime("%I:%M %p"),
            "question": user_text,
            "answer": ai_text
        }
    )

    # ---------------- Text To Speech ----------------

    with st.spinner("🔊 Generating Voice..."):

        audio_response = text_to_speech(ai_text)

    st.audio(
        audio_response,
        format="audio/mp3"
    )

    # ---------------- Download Answer ----------------

    st.download_button(
        label="📄 Download Response",
        data=ai_text,
        file_name="AYQ_Response.txt",
        mime="text/plain"
    )

    # ---------------- Download Voice ----------------

    st.download_button(
        label="🎵 Download Voice",
        data=audio_response.getvalue(),
        file_name="AYQ_Voice.mp3",
        mime="audio/mp3"
    )

# ---------------------------------------------------
# CONVERSATION HISTORY
# ---------------------------------------------------

st.divider()

st.subheader("💬 Conversation History")

if len(st.session_state.history) == 0:

    st.info("No conversation yet.")

else:

    for chat in reversed(st.session_state.history):

        st.markdown(
            f"""
            <div class="user-card">

            <b>👤 You</b>

            <br><br>

            {chat["question"]}

            <br><br>

            <small>{chat["time"]}</small>

            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            f"""
            <div class="ai-card">

            <b>🤖 AYQ</b>

            <br><br>

            {chat["answer"]}

            </div>
            """,
            unsafe_allow_html=True
        )

        st.write("")
# ---------------------------------------------------
# DASHBOARD
# ---------------------------------------------------

st.divider()

col1, col2, col3 = st.columns(3)

with col1:

    st.markdown(
        """
        <div class="stats">

        <h3>📊 Questions</h3>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.metric("", st.session_state.questions)

with col2:

    st.markdown(
        """
        <div class="stats">

        <h3>🌍 Language</h3>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.write(language.upper())

with col3:

    st.markdown(
        """
        <div class="stats">

        <h3>🎭 Personality</h3>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.write(personality)

# ---------------------------------------------------
# ABOUT
# ---------------------------------------------------

st.divider()

with st.expander("ℹ About AYQ"):

    st.markdown("""
### 🤖 AYQ

AYQ is an AI-powered Voice Assistant built using:

- 🎙 Streamlit
- 🧠 Groq API
- 🗣 Whisper Large V3 Turbo
- 🤖 Llama 3.3 70B Versatile
- 🔊 Google Text-to-Speech

Features

- ✅ Voice Recording
- ✅ Speech to Text
- ✅ AI Chat
- ✅ AI Voice Reply
- ✅ Conversation History
- ✅ Download Response
- ✅ Download Voice
- ✅ Multiple Personalities
- ✅ Multiple Languages

Developed for learning AI application development using Python and Streamlit.
""")

# ---------------------------------------------------
# QUICK TIPS
# ---------------------------------------------------

st.divider()

with st.expander("💡 Tips"):

    st.markdown("""
- Speak clearly.
- Keep your microphone close.
- Allow microphone permission in your browser.
- Use English for the best Whisper transcription accuracy.
""")

# ---------------------------------------------------
# FOOTER
# ---------------------------------------------------

st.markdown(
    """
    <div class="footer">

    <hr>

    <h4>🎙️ AYQ - AI Voice Assistant</h4>

    <p>
    Powered by Streamlit • Groq • Whisper • Llama • gTTS
    </p>

    <p>
    Version 2.0
    </p>

    </div>
    """,
    unsafe_allow_html=True
)
