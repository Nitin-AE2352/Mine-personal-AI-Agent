import streamlit as st
import json
import urllib.request
import urllib.error
import os

from chat_input_with_voice import (
    chat_input_with_voice,
    transcribe_audio
)

from voice import female_voice

from side import (
    initialize_chat,
    show_sidebar,
    save_current_chat,
    generate_chat_title
)


# =====================================
# APP SETTINGS
# =====================================

st.set_page_config(
    page_title="Mine AI With Nitin",
    page_icon="🤖",
    layout="wide"
)


# =====================================
# LOAD CSS
# =====================================

def load_css():

    css_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "Frontent",
        "frontend.css"
    )

    if os.path.isfile(css_path):

        with open(
            css_path,
            "r",
            encoding="utf-8"
        ) as file:

            st.markdown(
                f"<style>{file.read()}</style>",
                unsafe_allow_html=True
            )

    else:

        st.warning(
            f"CSS file nahi mili: {css_path}"
        )


load_css()


# =====================================
# INITIALIZE CHAT SYSTEM
# =====================================

initialize_chat()


# =====================================
# SHOW SIDEBAR
# =====================================

show_sidebar()


# =====================================
# AI SETTINGS
# =====================================

MODEL = "qwen2.5:1.5b"

URL = "http://localhost:11434/api/chat"

# Full chat history screen aur disk par rahegi.
# Ollama ko recent context hi bheja jayega.
MAX_CONTEXT_CHARACTERS = 12000


# =====================================
# AI PERSONALITY
# =====================================

SYSTEM_PROMPT = """
You are MyOwnAI, a smart personal AI assistant.

IMPORTANT LANGUAGE RULES:

1. Always reply in the same language and writing style
   used by the user.

2. If the user writes Hindi in English letters
   (Hinglish), reply in Hinglish using English letters.
   Example: "aap kaise ho" -> "main theek hoon".
   Never answer such a message in Hindi Devanagari or only English.

3. Never use Devanagari when the user writes Hinglish.

4. If the user writes Hindi in Devanagari,
   reply in Hindi Devanagari.

5. If the user writes in English,
   reply in English.
   Do not translate an English question into Hindi.

6. For mixed-language messages, use the user's dominant
   language and preserve the script they used.

7. Do not translate the user's language unnecessarily.

8. Keep answers natural, friendly and conversational.

9. Understand spelling mistakes and informal words.

10. Never invent personal information about the user.

11. Only use personal information provided by the user
    during the conversation.

12. If you don't know an answer, honestly say so.
"""

ROMAN_HINDI_WORDS = {
    "aap", "ap", "mai", "main", "mujhe", "mera", "meri", "mere",
    "hai", "hain", "ho", "kya", "kaise", "kaisa", "kyu", "kyon",
    "ko", "se", "me", "mein", "aur", "ye", "yah", "woh", "wo",
    "iska", "uska", "karna", "karo", "kuch", "batao", "chahiye",
    "nahi", "nahin", "acha", "accha", "kr", "do", "de", "dena",
    "puch", "pooch", "answer", "samjhao", "btao"
}


def detect_response_language(text):
    """User ki language aur script identify karta hai."""

    words = {
        word.strip(".,!?;:()[]{}\"'").lower()
        for word in text.split()
    }

    if any("\u0900" <= character <= "\u097f" for character in text):
        return "Hindi Devanagari"

    if len(words.intersection(ROMAN_HINDI_WORDS)) >= 2:
        return "Roman Hinglish (Hindi written using English letters)"

    return "English"


def build_model_context(messages):
    """Recent messages ko model context ke liye select karta hai."""

    context = []
    character_count = 0

    for message in reversed(messages):

        content = str(message.get("content", ""))
        message_size = len(content)

        if context and (
            character_count + message_size > MAX_CONTEXT_CHARACTERS
        ):
            break

        context.append({
            "role": message["role"],
            "content": content
        })

        character_count += message_size

    context.reverse()

    return context


# =====================================
# SESSION STATE INITIALIZATION
# =====================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "voice_text" not in st.session_state:
    st.session_state.voice_text = next(
        (
            message["content"]
            for message in reversed(st.session_state.messages)
            if message.get("role") == "assistant"
        ),
        ""
    )

if "voice_language" not in st.session_state:
    st.session_state.voice_language = "en-IN"

# Har submit ke baad is key ko increment karenge.
# Nayi key se custom input component fresh mount hoga.
if "chat_input_key" not in st.session_state:
    st.session_state.chat_input_key = 0


# =====================================
# MAIN APP INTERFACE
# =====================================

st.title("🤖 Mine AI Agent")

st.caption("Mine Personal AI Assistant")

if not st.session_state.messages:

    st.markdown(
        """
        <div class="home-search">
            <h2>How can I help you today?</h2>
            <p>Ask anything to MyOwnAI</p>
        </div>
        """,
        unsafe_allow_html=True
    )


# =====================================
# SHOW OLD CHAT MESSAGES
# =====================================

for message_index, message in enumerate(st.session_state.messages):

    with st.chat_message(message["role"]):

        st.markdown(message["content"])

        if message["role"] == "assistant":

            if st.button(
                "🔊 Female voice",
                key=f"speak_history_{message_index}"
            ):

                female_voice(
                    message["content"],
                    message.get("voice_language", "en-IN")
                )


# =====================================
# TEXT + VOICE INPUT
# =====================================

voice_result = chat_input_with_voice(
    key=f"chat_input_{st.session_state.chat_input_key}"
)

prompt = None

if voice_result:

    event_id = voice_result.get("event_id")

    # Ek hi component event ko dobara process nahi karna.
    if event_id and (
        event_id != st.session_state.get("last_voice_input_event")
    ):

        st.session_state.last_voice_input_event = event_id

        if voice_result.get("type") == "text":

            prompt = voice_result.get("text", "").strip()

        elif voice_result.get("type") == "audio":

            with st.spinner("Listening to your voice..."):

                prompt = transcribe_audio(
                    voice_result.get("audio"),
                    voice_result.get("mime_type", "audio/webm")
                )

            if prompt and (
                prompt.startswith("Audio processing error:")
                or prompt.startswith("Speech recognition service error:")
            ):

                st.error(prompt)
                prompt = None


# =====================================
# PROCESS USER MESSAGE
# =====================================

if prompt:

    response_language = detect_response_language(prompt)

    # ---------------------------------
    # FIRST MESSAGE = CHAT TITLE
    # ---------------------------------

    if len(st.session_state.messages) == 0:

        try:

            st.session_state.chat_title = generate_chat_title(prompt)

        except Exception:

            st.session_state.chat_title = prompt[:40]


    # ---------------------------------
    # SAVE USER MESSAGE
    # ---------------------------------

    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    save_current_chat()


    # ---------------------------------
    # SHOW USER MESSAGE
    # ---------------------------------

    with st.chat_message("user"):

        st.markdown(prompt)


    # ---------------------------------
    # CREATE CONVERSATION
    # ---------------------------------

    language_instruction = {
        "role": "system",
        "content": (
            f"Respond strictly in {response_language}. "
            "Do not switch to English unless the user used English. "
            "For Roman Hinglish, use natural Hindi words in English letters "
            "and do not use Devanagari."
        )
    }

    conversation = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },
        language_instruction
    ] + build_model_context(st.session_state.messages)


    # ---------------------------------
    # OLLAMA REQUEST DATA
    # ---------------------------------

    data = {
        "model": MODEL,
        "messages": conversation,
        "stream": False,
        "options": {
            "num_ctx": 8192
        }
    }


    # ---------------------------------
    # CREATE API REQUEST
    # ---------------------------------

    request = urllib.request.Request(
        URL,
        data=json.dumps(data).encode("utf-8"),
        headers={
            "Content-Type": "application/json"
        },
        method="POST"
    )


    # =================================
    # AI RESPONSE
    # =================================

    with st.chat_message("assistant"):

        with st.spinner("MyOwnAI is thinking..."):

            try:

                with urllib.request.urlopen(
                    request,
                    timeout=180
                ) as response:

                    result = json.loads(
                        response.read().decode("utf-8").strip()
                    )

                answer = result.get("message", {}).get(
                    "content",
                    ""
                ).strip()

                if not answer:

                    raise ValueError(
                        "Ollama ne empty response bheja."
                    )


                # ---------------------------------
                # SAVE LAST ANSWER FOR VOICE
                # ---------------------------------

                st.session_state.voice_text = answer

                st.session_state.voice_language = (
                    "hi-IN"
                    if response_language.startswith("Roman Hinglish")
                    else "en-IN"
                )


                # ---------------------------------
                # SHOW AI ANSWER
                # ---------------------------------

                st.markdown(answer)


                # ---------------------------------
                # SAVE AI MESSAGE
                # ---------------------------------

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "voice_language": st.session_state.voice_language
                })

                save_current_chat()


            except urllib.error.URLError as error:

                error_message = (
                    "Ollama connection nahi ho pa raha hai. "
                    "Please Ollama ko check karke dobara try karein."
                )

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_message,
                    "voice_language": "en-IN"
                })

                save_current_chat()

                st.error(error_message)
                st.caption(str(error))


            except Exception as error:

                error_message = (
                    "AI response generate nahi ho paya. "
                    "Aapka question save hai; dobara try karein."
                )

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_message,
                    "voice_language": "en-IN"
                })

                save_current_chat()

                st.error(error_message)
                st.caption(str(error))


    # ---------------------------------
    # RESET INPUT FOR NEXT QUESTION
    # ---------------------------------

    # Fresh key se component ka previous input/event reset hoga.
    st.session_state.chat_input_key += 1

    # Updated chat aur fresh input dikhane ke liye rerun.
    st.rerun()


# =====================================
# SPEAK LAST ANSWER
# =====================================

if st.session_state.voice_text:

    if st.button(
        "🔊 Speak Last Answer",
        key="speak_last_answer"
    ):

        female_voice(
            st.session_state.voice_text,
            st.session_state.voice_language
        )