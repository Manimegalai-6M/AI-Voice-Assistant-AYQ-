import os
from io import BytesIO
from datetime import datetime
import streamlit as st
from dotenv import load_dotenv
from groq import Groq
from gtts import gTTS
import hashlib
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

<style>

/* ==========================
   GOOGLE FONT
========================== */
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

html,
body,
.stApp{
    font-family:'Poppins',sans-serif;
    color:white;
    overflow-x:hidden;

    background:linear-gradient(
    -45deg,
    #0F172A,
    #1E293B,
    #312E81,
    #0F766E,
    #7C3AED
    );

    background-size:500% 500%;
    animation:gradientBG 18s ease infinite;
}

/* Animated Background */

@keyframes gradientBG{

0%{
background-position:0% 50%;
}

50%{
background-position:100% 50%;
}

100%{
background-position:0% 50%;
}

}


/* ==========================
SIDEBAR
========================== */

section[data-testid="stSidebar"]{

background:rgba(17,24,39,.85);

backdrop-filter:blur(20px);

border-right:1px solid rgba(255,255,255,.08);

}


/* ==========================
HERO
========================== */

.hero{

background:rgba(255,255,255,.08);

backdrop-filter:blur(20px);

padding:45px;

border-radius:25px;

border:1px solid rgba(255,255,255,.15);

box-shadow:

0 10px 40px rgba(0,0,0,.45),

0 0 30px rgba(124,58,237,.35);

animation:floatHero 4s ease-in-out infinite;

margin-bottom:30px;

}

.hero h1{

font-size:56px;

font-weight:700;

background:linear-gradient(
90deg,
#60A5FA,
#A855F7,
#22D3EE,
#F472B6
);

-webkit-background-clip:text;

-webkit-text-fill-color:transparent;

}

.hero p{

font-size:22px;

color:#E2E8F0;

}

@keyframes floatHero{

0%{transform:translateY(0px);}

50%{transform:translateY(-8px);}

100%{transform:translateY(0px);}

}


/* ==========================
USER CARD
========================== */

.user-card{

background:rgba(59,130,246,.12);

border:1px solid rgba(96,165,250,.35);

border-left:6px solid #3B82F6;

backdrop-filter:blur(20px);

padding:22px;

border-radius:20px;

margin-top:18px;

transition:.35s;

box-shadow:0 8px 20px rgba(0,0,0,.25);

}

.user-card:hover{

transform:translateY(-6px) scale(1.02);

box-shadow:0 0 35px rgba(59,130,246,.45);

}


/* ==========================
AI CARD
========================== */

.ai-card{

background:rgba(168,85,247,.10);

border:1px solid rgba(168,85,247,.30);

border-left:6px solid #A855F7;

backdrop-filter:blur(20px);

padding:22px;

border-radius:20px;

margin-top:18px;

transition:.35s;

box-shadow:0 8px 20px rgba(0,0,0,.25);

}

.ai-card:hover{

transform:translateY(-6px) scale(1.02);

box-shadow:0 0 35px rgba(168,85,247,.45);

}


/* ==========================
BUTTONS
========================== */

.stButton>button{

width:100%;

border-radius:14px;

border:none;

font-weight:600;

padding:12px;

background:linear-gradient(
90deg,
#3B82F6,
#8B5CF6
);

color:white;

transition:.35s;

}

.stButton>button:hover{

transform:scale(1.04);

box-shadow:

0 0 25px rgba(139,92,246,.55);

}


/* ==========================
DOWNLOAD BUTTON
========================== */

.stDownloadButton>button{

width:100%;

border-radius:14px;

background:linear-gradient(
90deg,
#06B6D4,
#3B82F6
);

color:white;

border:none;

font-weight:600;

}


/* ==========================
METRICS
========================== */

.stats{

background:rgba(255,255,255,.08);

backdrop-filter:blur(20px);

padding:25px;

border-radius:20px;

text-align:center;

border:1px solid rgba(255,255,255,.12);

transition:.3s;

}

.stats:hover{

transform:translateY(-6px);

box-shadow:0 0 25px rgba(34,211,238,.35);

}


/* ==========================
SCROLLBAR
========================== */

::-webkit-scrollbar{

width:10px;

}

::-webkit-scrollbar-thumb{

background:linear-gradient(
#3B82F6,
#A855F7
);

border-radius:50px;

}

::-webkit-scrollbar-track{

background:#111827;

}


/* ==========================
FOOTER
========================== */

.footer{

margin-top:60px;

padding:25px;

text-align:center;

color:#CBD5E1;

border-top:1px solid rgba(255,255,255,.08);

}


/* ==========================
FADE ANIMATION
========================== */

@keyframes fade{

from{

opacity:0;

transform:translateY(15px);

}

to{

opacity:1;

transform:translateY(0);

}

}

.hero,
.user-card,
.ai-card,
.stats{

animation:fade .8s ease;

}

</style>
# ---------------------------------------------------
# LOAD ENV
# ---------------------------------------------------

load_dotenv()

groq_api_key = os.getenv("GROQ_API_KEY")

if not groq_api_key:
    st.error("GROQ_API_KEY not found.")
    st.stop()

client = Groq(api_key=groq_api_key)

# ---------------------------------------------------
# SESSION STATE
# ---------------------------------------------------

if "history" not in st.session_state:
    st.session_state.history = []

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system",
            "content": "You are a friendly AI assistant."
        }
    ]
if "questions" not in st.session_state:
    st.session_state.questions = 0
if "last_audio_id" not in st.session_state:
    st.session_state.last_audio_id = None
# ---------------------------------------------------
# SYSTEM PROMPTS
# ---------------------------------------------------

SYSTEM_PROMPTS = {

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
# SIDEBAR
# ---------------------------------------------------

with st.sidebar:

    st.title("🤖 AYQ")

    st.write("Your Personal AI Assistant")

    st.divider()

    personality = st.selectbox(
        "AI Personality",
        [
            "General Assistant",
            "Teacher",
            "Programmer",
            "Motivator",
            "Interviewer"
        ]
    )

    language_name = st.selectbox(
        "Voice Language",
        [
            "English",
            "Tamil",
            "Hindi"
        ]
    )

    language_map = {
        "English": "en",
        "Tamil": "ta",
        "Hindi": "hi"
    }

    language = language_map[language_name]

    temperature = st.slider(
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
        "Conversations Count",
        len(st.session_state.history)
    )

    st.divider()

    if st.button("🗑 Clear Conversation"):
        st.session_state.messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPTS[personality]
            }
        ]

        st.session_state.history = []

        st.session_state.questions = 0

        st.session_state.last_audio_id = None
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
# FUNCTIONS
# ---------------------------------------------------

def generate_ai(user_text):

    # Update system prompt
    st.session_state.messages[0] = {
        "role": "system",
        "content": SYSTEM_PROMPTS[personality]
    }

    # Add user message
    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_text
        }
    )

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=st.session_state.messages,
        temperature=float(temperature),
        max_tokens=700
    )

    ai_text = (response.choices[0].message.content or"Sorry, I couldn't generate a response.").strip()

    # Save AI reply
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": ai_text
        }
    )

    MAX_HISTORY = 50

    if len(st.session_state.messages) > MAX_HISTORY:
        st.session_state.messages = (
            [st.session_state.messages[0]]
            + st.session_state.messages[-(MAX_HISTORY - 1):]
        )
    return ai_text


def text_to_speech(text):
    try:
        audio = BytesIO()

        tts = gTTS(
            text=text[:3000],
            lang=language
        )

        tts.write_to_fp(audio)

        audio.seek(0)

        return audio

    except Exception:
        st.error("Unable to generate voice. Please try again.")
        return None

def speech_to_text(audio_bytes):
    try:
        transcript = client.audio.transcriptions.create(
            file=("audio.wav", audio_bytes),
            model="whisper-large-v3-turbo",
            response_format="json"
        )
        return transcript.text
    except Exception:
        st.error("Unable to recognize your voice. Please try again.")
        return ""
        
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

    current_audio_id = hashlib.md5(audio_value.getvalue()).hexdigest()

    if st.session_state.last_audio_id == current_audio_id:
        st.stop()

    st.session_state.last_audio_id = current_audio_id

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
        unsafe_allow_html = True
    )

    # Save question count

    st.session_state.questions += 1

    # ---------------- AI Response ----------------
    with st.spinner("🧠 AYQ is thinking..."):
        try:
            ai_text = generate_ai(user_text)
        except Exception as e:
            st.error(f"AI Error: {e}")
            st.stop()
            
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

    # Keep only the latest 100 conversations
    st.session_state.history = st.session_state.history[-100:]
    # ---------------- Text To Speech ----------------
    audio_response = None
    with st.spinner("🔊 Generating Voice..."):
        try:
            audio_response = text_to_speech(ai_text)

            if audio_response:
                st.audio(audio_response, format="audio/mp3")

        except Exception:
            st.error("Voice generation failed.")
    # ---------------- Download Answer ----------------

    st.download_button(
        label="📄 Download Response",
        data=ai_text,
        file_name="AYQ_Response.txt",
        mime="text/plain"
    )

    if audio_response is not None:
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

    st.write(language_name)

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

    <h4>🎙️ AYQ - Ask Your Questions </h4>

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
