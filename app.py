import streamlit as st
from audio_recorder_streamlit import audio_recorder
import openai
import base64
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
def setup_openai_client(api_key):
    return openai.OpenAI(api_key=api_key)

# Function to transcribe audio to text
def transcribe_audio(client, audio_path):
    with open(audio_path, 'rb') as audio_file: 
        transcript = client.audio.transcriptions.create(model="whisper-1", file=audio_file)
        return transcript.text

# Taking response from OpenAI
def fetch_ai_response(client, input_text):
    messages = [{"role": "user", "content": input_text}]
    response = client.chat.completions.create(model='gpt-3.5-turbo-1106', messages=messages)
    return response.choices[0].message.content

# Convert text to audio
def text_to_audio(client, text, audio_path):
    response = client.audio.speech.create(model="tts-1", voice="nova", input=text)
    response.stream_to_file(audio_path)

# Text cards functions
def create_text_card(text, title="Response"):
    card_html = f"""
    <style>
        .card {{
            box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2);
            transition: 0.3s;
            border-radius: 10px;
            padding: 20px;
            background-color: #f9f9f9;
            margin-top: 20px;
            color: black; /* Ensures text is always black */
            text-align: left; /* Align text to the left */
            direction: ltr; /* Ensures text direction is left-to-right */
            font-family: Arial, sans-serif;
        }}
        .card:hover {{
            box-shadow: 0 8px 16px 0 rgba(0,0,0,0.2);
        }}
        .container {{
            padding: 10px 20px;
        }}
    </style>
    <div class="card">
        <div class="container">
            <h4 style="color: #4CAF50;"><b>{title}</b></h4>
            <p>{text}</p>
        </div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)


# AUTO-play audio
import time

def auto_play_audio(audio_file):
    with open(audio_file, 'rb') as audio_file:
        audio_bytes = audio_file.read()
    base64_audio = base64.b64encode(audio_bytes).decode("utf-8")
    audio_html = f'<audio src="data:audio/mp3;base64,{base64_audio}" controls autoplay>'
    st.markdown(audio_html, unsafe_allow_html=True)


def main():
    # Set page configuration
    st.set_page_config(
        page_title="EduGenie - AI Study Assistant",
        page_icon="🎓",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Add logo and title
    logo_path = r"https://github.com/KevinFoyet/EduGenie/blob/main/EduGenie%20Logo.webp"

    # Create a centered layout using columns
    col1, col2, col3 = st.columns([3, 5, 3])  # Adjust column widths for centering
    with col1:
        st.empty()  # Left empty for spacing
    with col2:
        st.image(logo_path, width=400, use_container_width=False)
    with col3:
        st.empty()  # Right empty for spacing


    st.markdown(
        """
        <h1 style="text-align: center; color: #4CAF50; font-size: 3em;">EduGenie</h1>
        <p style="text-align: center; font-size: 1.2em; color: #555;">
            Hi there! This is EduGenie, your favorite AI study assistant. Practice the Feynman Technique with me!
        </p>
        <hr style="border: 1px solid #4CAF50;">
        """,
        unsafe_allow_html=True,
    )

    # Sidebar for API Key configuration
    st.sidebar.title("🔑 API Key Configuration")
    st.sidebar.markdown(
        """
        Enter your OpenAI API Key below to unlock EduGenie's features. 
        Your key is stored securely and only used for this session.
        """
    )
    api_key = st.sidebar.text_input("Enter your OpenAI API Key", type="password")

    if api_key:
        client = setup_openai_client(api_key)

        # Audio Recorder
        st.markdown(
            """
            <h2 style="color: #4CAF50;">🎙️ Record Your Voice</h2>
            <p style="color: #555;">Click the button below to record your voice and let EduGenie process it for insights!</p>
            """,
            unsafe_allow_html=True,
        )
        recorded_audio = audio_recorder()

        # Process Recorded Audio
        if recorded_audio:
            st.success("Audio recorded successfully!")
            audio_file = "audio.mp3"
            with open(audio_file, 'wb') as f:
                f.write(recorded_audio)

            # Transcribe and display text
            transcribed_text = transcribe_audio(client, audio_file)
            create_text_card(transcribed_text, "Transcribed Text")

            # Fetch AI response
            ai_response = fetch_ai_response(client, transcribed_text)
            response_audio_file = "audio_response.mp3"
            text_to_audio(client, ai_response, response_audio_file)

            # Play AI response audio
            auto_play_audio(response_audio_file)
            create_text_card(ai_response, "AI Response")

if __name__ == "__main__":
    main()
