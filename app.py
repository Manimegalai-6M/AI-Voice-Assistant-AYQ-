import os
import json
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

html, body, [class*="css"] {
    background:#0F172A;
    color:white;
}


/* Main background */

.main {
    background:#0F172A;
}


/* Sidebar */

section[data-testid="stSidebar"] {
    background:#111827;
}


/* Hero Section */

.hero {

    background:linear-gradient(
        90deg,
        #2563EB,
        #7C3AED
    );

    padding:35px;

    border-radius:20px;

    text-align:center;

    margin-bottom:20px;

    box-shadow:
    0px 10px 30px rgba(0,0,0,0.35);

}


.hero h1 {

    color:white;

    font-size:48px;

}


.hero p {

    color:#E5E7EB;

    font-size:20px;

}


/* User Message Card */

.user-card {

    background:#1E293B;

    padding:18px;

    border-radius:15px;

    margin-top:15px;

    border-left:
    6px solid #3B82F6;

}


/* AI Response Card */

.ai-card {

    background:#162033;

    padding:18px;

    border-radius:15px;

    margin-top:15px;

    border-left:
    6px solid #8B5CF6;

}


/* Statistics Cards */

.stats {

    background:#111827;

    border-radius:15px;

    padding:18px;

    text-align:center;

}


/* Footer */

.footer {

    margin-top:50px;

    text-align:center;

    color:#94A3B8;

    font-size:14px;

}


/* Divider */

hr {

    border:
    1px solid #374151;

}


/* Buttons */

.stButton button {

    width:100%;

    border-radius:10px;

    font-size:18px;

}


/* Audio Player */

audio {

    width:100%;

}


</style>

""", unsafe_allow_html=True)

# ---------------------------------------------------
# LOAD ENV
# ---------------------------------------------------

load_dotenv()


# Get Groq API Key
# First check Streamlit Cloud secrets
# Then check local .env file

groq_api_key = (
    st.secrets.get("GROQ_API_KEY")
    if "GROQ_API_KEY" in st.secrets
    else os.getenv("GROQ_API_KEY")
)


# Check API Key

if not groq_api_key:

    st.error(
        "❌ GROQ_API_KEY not found. "
        "Please add it in Streamlit Secrets or .env file."
    )

    st.stop()


# Initialize Groq Client

client = Groq(
    api_key=groq_api_key
)

# ---------------------------------------------------
# SESSION STATE
# ---------------------------------------------------

# Store conversation history

if "history" not in st.session_state:

    st.session_state.history = []


# Count total questions

if "questions" not in st.session_state:

    st.session_state.questions = 0


# Store current audio processing status

if "processing" not in st.session_state:

    st.session_state.processing = False
# ---------------------------------------------------
# SIDEBAR
# ---------------------------------------------------

with st.sidebar:

    st.title("🤖 AYQ")

    st.write(
        "Your Personal AI Voice Assistant"
    )

    st.divider()


    # AI Personality Selection

    personality = st.selectbox(
        "🎭 AI Personality",
        [
            "General Assistant",
            "Teacher",
            "Programmer",
            "Motivator",
            "Interviewer"
        ]
    )


    # Voice Language Selection

    language = st.selectbox(
        "🌍 Voice Language",
        {
            "English": "en",
            "Tamil": "ta",
            "Hindi": "hi"
        }
    )


    # Creativity Level

    temperature = st.slider(
        "🧠 Creativity",
        min_value=0.0,
        max_value=1.0,
        value=0.3,
        step=0.1
    )


    st.divider()


    # Statistics

    st.subheader("📊 Statistics")


    st.metric(
        "Questions",
        st.session_state.questions
    )


    st.metric(
        "Conversation",
        len(st.session_state.history)
    )


    st.divider()


    # Clear Chat Button

    if st.button("🗑 Clear Conversation"):


        st.session_state.history = []


        st.session_state.questions = 0


        st.session_state.processing = False


        st.success(
            "Conversation cleared!"
        )


        st.rerun()
# ---------------------------------------------------
# HERO
# ---------------------------------------------------

st.markdown(
    """
    <div class="hero">

        <h1>🎙️ AYQ</h1>

        <p>
            Your Personal AI Voice Assistant
        </p>

        <p>
            🎤 Speak • 🧠 Think • 🔊 Respond
        </p>

    </div>
    """,
    unsafe_allow_html=True
)

# ---------------------------------------------------
# SYSTEM PROMPTS
# ---------------------------------------------------

SYSTEM_PROMPTS = {

    "General Assistant":
    """
    You are AYQ, a friendly AI voice assistant.
    Answer clearly and helpfully.
    Keep responses simple and easy to understand.
    """,


    "Teacher":
    """
    You are a patient teacher.
    Explain concepts step-by-step with simple examples.
    Help users learn easily.
    """,


    "Programmer":
    """
    You are a senior software engineer.
    Give accurate programming explanations.
    Provide clean code examples when needed.
    Explain errors and solutions clearly.
    """,


    "Motivator":
    """
    You are a positive motivational coach.
    Encourage users and provide practical advice.
    Keep your tone supportive.
    """,


    "Interviewer":
    """
    You are an AI interviewer.
    Ask professional follow-up questions.
    Evaluate answers and provide feedback.
    Simulate a real interview experience.
    """

}
# ---------------------------------------------------
# PROCESS AUDIO
# ---------------------------------------------------

# ---------------------------------------------------
# FUNCTIONS
# ---------------------------------------------------


# ---------------- AI CHAT FUNCTION ----------------

def generate_ai(question):

    messages = [

        {
            "role": "system",
            "content": SYSTEM_PROMPTS[personality]
        }

    ]


    # Add previous conversation memory

    for chat in st.session_state.history:

        messages.append(
            {
                "role": "user",
                "content": chat["question"]
            }
        )


        messages.append(
            {
                "role": "assistant",
                "content": chat["answer"]
            }
        )


    # Add current question

    messages.append(
        {
            "role": "user",
            "content": question
        }
    )


    response = client.chat.completions.create(

        model="llama-3.3-70b-versatile",

        messages=messages,

        temperature=temperature,

        max_tokens=400

    )


    return response.choices[0].message.content



# ---------------- TEXT TO SPEECH FUNCTION ----------------

def text_to_speech(text):

    audio = BytesIO()


    tts = gTTS(

        text=text,

        lang=language

    )


    tts.write_to_fp(audio)


    audio.seek(0)


    return audio



# ---------------- SPEECH TO TEXT FUNCTION ----------------

def speech_to_text(audio_bytes):

    transcript = client.audio.transcriptions.create(

        file=(
            "audio.wav",
            audio_bytes
        ),

        model="whisper-large-v3-turbo",

        response_format="json"

    )


    return transcript.text



# ---------------- SAVE HISTORY FUNCTION ----------------

def save_history():

    with open(
        "history.json",
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(

            st.session_state.history,

            f,

            indent=4,

            ensure_ascii=False

        )
# ---------------------------------------------------
# MAIN INTERFACE
# ---------------------------------------------------

st.subheader("🎤 Ask using your voice")

st.write(
    "Record your question and click Ask AYQ."
)


# Voice Recorder

audio_value = st.audio_input(
    "🎙️ Record your question"
)


# Ask Button

ask_button = st.button(
    "🚀 Ask AYQ"
)



# ---------------------------------------------------
# PROCESS AUDIO
# ---------------------------------------------------

if audio_value is not None and ask_button:


    audio_bytes = audio_value.getvalue()


    # Check empty audio

    if len(audio_bytes) == 0:

        st.warning(
            "No audio detected."
        )

        st.stop()



    # Show recorded audio

    st.audio(
        audio_value
    )



    # ---------------- SPEECH TO TEXT ----------------


    with st.spinner(
        "🎧 Listening..."
    ):

        try:

            user_text = speech_to_text(
                audio_bytes
            )


        except Exception as e:

            st.error(
                f"Speech recognition failed.\n\n{e}"
            )

            st.stop()



    if not user_text.strip():

        st.warning(
            "No speech detected."
        )

        st.stop()



    # ---------------- SHOW USER QUESTION ----------------


    st.markdown(

        f"""

        <div class="user-card">

        <h4>👤 You</h4>

        <p>{user_text}</p>

        </div>

        """,

        unsafe_allow_html=True

    )



    # Increase question count

    st.session_state.questions += 1




    # ---------------- AI RESPONSE ----------------


    with st.spinner(
        "🧠 AYQ is thinking..."
    ):


        ai_text = generate_ai(
            user_text
        )



    # ---------------- SHOW AI ANSWER ----------------


    st.markdown(

        f"""

        <div class="ai-card">

        <h4>🤖 AYQ</h4>

        <p>{ai_text}</p>

        </div>

        """,

        unsafe_allow_html=True

    )



    # ---------------- SAVE CONVERSATION ----------------


    st.session_state.history.append(

        {

            "time":
            datetime.now().strftime("%I:%M %p"),

            "question":
            user_text,

            "answer":
            ai_text

        }

    )


    # Save JSON file

    save_history()




    # ---------------- TEXT TO SPEECH ----------------


    with st.spinner(
        "🔊 Generating Voice..."
    ):


        audio_response = text_to_speech(
            ai_text
        )



    st.audio(

        audio_response,

        format="audio/mp3"

    )



    # ---------------- DOWNLOAD RESPONSE ----------------


    st.download_button(

        label="📄 Download Response",

        data=ai_text,

        file_name="AYQ_Response.txt",

        mime="text/plain"

    )



    # ---------------- DOWNLOAD VOICE ----------------


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


st.subheader(
    "💬 Conversation History"
)


if len(st.session_state.history) == 0:


    st.info(
        "No conversation yet. Start asking AYQ!"
    )


else:


    for chat in reversed(
        st.session_state.history
    ):


        # User message

        st.markdown(

            f"""

            <div class="user-card">


            <b>👤 You</b>


            <br><br>


            {chat["question"]}


            <br><br>


            <small>
            🕒 {chat["time"]}
            </small>


            </div>

            """,

            unsafe_allow_html=True

        )



        # AI response

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


st.subheader(
    "📊 AYQ Dashboard"
)


col1, col2, col3 = st.columns(3)



# ---------------- Questions ----------------

with col1:


    st.markdown(

        """

        <div class="stats">

        <h3>📊 Questions</h3>

        </div>

        """,

        unsafe_allow_html=True

    )


    st.metric(

        label="",

        value=st.session_state.questions

    )



# ---------------- Language ----------------

with col2:


    st.markdown(

        """

        <div class="stats">

        <h3>🌍 Language</h3>

        </div>

        """,

        unsafe_allow_html=True

    )


    st.write(

        language.upper()

    )



# ---------------- Personality ----------------

with col3:


    st.markdown(

        """

        <div class="stats">

        <h3>🎭 Personality</h3>

        </div>

        """,

        unsafe_allow_html=True

    )


    st.write(

        personality

    )
# ---------------------------------------------------
# ABOUT AYQ
# ---------------------------------------------------

st.divider()


with st.expander(
    "ℹ️ About AYQ"
):


    st.markdown(
        """

## 🤖 AYQ - AI Voice Assistant


AYQ is an AI-powered voice assistant application built using
modern Generative AI technologies.


### 🚀 Technologies Used


- 🎙️ **Streamlit**  
  User interface and web application framework


- 🧠 **Groq API**  
  Fast AI inference engine


- 🤖 **Llama 3.3 70B Versatile**  
  Large Language Model for intelligent conversations


- 🗣️ **Whisper Large V3 Turbo**  
  Speech-to-Text voice recognition


- 🔊 **Google Text-to-Speech (gTTS)**  
  AI voice response generation



### ✨ Features


✅ Voice Recording

✅ Speech to Text Conversion

✅ AI Chat Assistant

✅ AI Voice Reply

✅ Conversation Memory

✅ Conversation History

✅ Download Text Response

✅ Download Voice Response

✅ Multiple AI Personalities

✅ Multiple Languages

✅ AI Chat Memory



### 🎯 Project Goal


AYQ was developed to learn and demonstrate
AI application development using Python,
Streamlit, Speech AI, and Large Language Models.


### 🔮 Future Improvements


- 🎨 AI Avatar

- 🌊 Animated Voice Waveform

- 😊 AI Emotion Detection

- 🌐 Real-time Translation

- 🖼️ AI Image Generation

- 📱 Mobile Application


"""

    )

# ---------------------------------------------------
# QUICK TIPS
# ---------------------------------------------------

st.divider()


with st.expander(
    "💡 Quick Tips"
):

    st.markdown(
        """

### 🎤 Voice Recording Tips


✅ Speak clearly and slowly.

✅ Keep your microphone close.

✅ Avoid background noise.

✅ Give complete questions for better answers.

✅ Allow microphone permission in your browser.



### 🌍 Language Tips


✅ English gives the best Whisper accuracy.

✅ Tamil and Hindi voice responses are supported.

✅ Select the correct voice language before asking.



### 🤖 AI Response Tips


✅ Choose the right AI personality.

✅ Programmer mode is useful for coding questions.

✅ Teacher mode is useful for learning concepts.

✅ Interviewer mode helps practice interviews.



### ⚡ Performance Tips


✅ Use a stable internet connection.

✅ Wait until AYQ finishes responding before asking another question.

✅ Clear conversation when starting a new topic.

"""
    )

# ---------------------------------------------------
# FOOTER
# ---------------------------------------------------

st.markdown(
    """

    <div class="footer">

        <hr>

        <h4>
        🎙️ AYQ - AI Voice Assistant
        </h4>


        <p>
        Powered by Streamlit • Groq • Whisper • Llama • gTTS
        </p>


        <p>
        🚀 Version 2.0 | Built with Python & Generative AI
        </p>


        <p>
        © 2026 AYQ. All rights reserved.
        </p>


    </div>

    """,

    unsafe_allow_html=True
)
