import os
import base64
import io

import streamlit as st
import streamlit.components.v1 as components
import speech_recognition as sr


# -----------------------------------------
# COMPONENT FOLDER
# -----------------------------------------

COMPONENT_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "Frontent"
)

# Check that component HTML exists
INDEX_FILE = os.path.join(COMPONENT_DIR, "index.html")

if not os.path.isfile(INDEX_FILE):
    raise FileNotFoundError(
        f"Component file not found: {INDEX_FILE}"
    )


# -----------------------------------------
# DECLARE STREAMLIT COMPONENT
# -----------------------------------------

voice_chat_component = components.declare_component(
    "voice_chat_input",
    path=COMPONENT_DIR
)


# -----------------------------------------
# TEXT + VOICE INPUT
# -----------------------------------------

def chat_input_with_voice(key="myownai_voice_input"):

    return voice_chat_component(
        key=key,
        default=None,
        height=105
    )


# -----------------------------------------
# AUDIO TO TEXT
# -----------------------------------------

def transcribe_audio(audio_base64, mime_type="audio/webm"):

    try:
        if not audio_base64:
            return "Audio data nahi mila."

        audio_bytes = base64.b64decode(audio_base64)

        from pydub import AudioSegment

        audio_format = "webm"

        if "ogg" in mime_type:
            audio_format = "ogg"
        elif "mp4" in mime_type:
            audio_format = "mp4"

        audio = AudioSegment.from_file(
            io.BytesIO(audio_bytes),
            format=audio_format
        )

        wav_buffer = io.BytesIO()

        audio.export(
            wav_buffer,
            format="wav"
        )

        wav_buffer.seek(0)

        recognizer = sr.Recognizer()

        with sr.AudioFile(wav_buffer) as source:
            recorded_audio = recognizer.record(source)

        return recognizer.recognize_google(
            recorded_audio,
            language="hi-IN"
        )

    except sr.UnknownValueError:
        return "Audio samajh nahi aaya. Dobara boliye."

    except sr.RequestError as error:
        return f"Speech recognition service error: {error}"

    except Exception as error:
        return f"Audio processing error: {error}"