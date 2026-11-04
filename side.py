import streamlit as st
import json
import os
import uuid
from datetime import datetime


# =====================================
# CHAT HISTORY FOLDER
# =====================================

CHAT_FOLDER = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "chats"
)

if not os.path.exists(CHAT_FOLDER):
    os.makedirs(CHAT_FOLDER)


# =====================================
# GET ALL CHAT FILES
# =====================================

def get_chat_files():

    files = []

    for file in os.listdir(CHAT_FOLDER):

        if file.endswith(".json"):
            files.append(file)

    # Latest chat sabse upar
    files.sort(
        key=lambda x: os.path.getmtime(
            os.path.join(CHAT_FOLDER, x)
        ),
        reverse=True
    )

    return files


# =====================================
# CREATE NEW CHAT
# =====================================

def create_new_chat():

    chat_id = str(uuid.uuid4())

    chat_data = {
        "id": chat_id,
        "title": "New Chat",
        "created_at": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        "messages": []
    }

    file_path = os.path.join(
        CHAT_FOLDER,
        f"{chat_id}.json"
    )

    with open(
        file_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            chat_data,
            file,
            ensure_ascii=False,
            indent=2
        )

    return chat_id


# =====================================
# LOAD CHAT
# =====================================

def load_chat(chat_id):

    file_path = os.path.join(
        CHAT_FOLDER,
        f"{chat_id}.json"
    )

    if os.path.exists(file_path):

        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    return None


# =====================================
# SAVE CURRENT CHAT
# =====================================

def save_current_chat():

    if "current_chat_id" not in st.session_state:
        return

    chat_data = {

        "id": st.session_state.current_chat_id,

        "title": st.session_state.get(
            "chat_title",
            "New Chat"
        ),

        "created_at": st.session_state.get(
            "created_at",
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        ),

        "messages": st.session_state.get(
            "messages",
            []
        )
    }

    file_path = os.path.join(
        CHAT_FOLDER,
        f"{st.session_state.current_chat_id}.json"
    )

    with open(
        file_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            chat_data,
            file,
            ensure_ascii=False,
            indent=2
        )


# =====================================
# GENERATE CHAT TITLE
# =====================================

def generate_chat_title(message):

    message = message.strip()

    if len(message) > 35:
        return message[:35] + "..."

    return message


# =====================================
# DELETE CHAT
# =====================================

def delete_chat(chat_id):

    file_path = os.path.join(
        CHAT_FOLDER,
        f"{chat_id}.json"
    )

    if os.path.exists(file_path):
        os.remove(file_path)


# =====================================
# INITIALIZE CHAT
# =====================================

def initialize_chat():

    if "current_chat_id" not in st.session_state:

        chat_files = get_chat_files()

        if chat_files:
            chat_id = chat_files[0].replace(".json", "")
            chat_data = load_chat(chat_id)

            if chat_data:
                st.session_state.current_chat_id = chat_id
                st.session_state.messages = chat_data.get(
                    "messages",
                    []
                )
                st.session_state.chat_title = chat_data.get(
                    "title",
                    "New Chat"
                )
                st.session_state.created_at = chat_data.get(
                    "created_at",
                    datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                )
                return

        # Create the first chat only when no saved chat exists.
        chat_id = create_new_chat()
        st.session_state.current_chat_id = chat_id
        st.session_state.messages = []
        st.session_state.chat_title = "New Chat"
        st.session_state.created_at = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )


# =====================================
# SHOW SIDEBAR
# =====================================

def show_sidebar():

    with st.sidebar:

        st.title("🤖 Mine AI")

        # -----------------------------
        # NEW CHAT BUTTON
        # -----------------------------

        if st.button(
            "➕ New Chat",
            use_container_width=True
        ):

            chat_id = create_new_chat()

            st.session_state.current_chat_id = chat_id
            st.session_state.messages = []
            st.session_state.chat_title = "New Chat"

            st.session_state.created_at = (
                datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            )

            st.rerun()


        st.divider()

        st.subheader("💬 Chat History")


        # -----------------------------
        # SHOW ALL CHATS
        # -----------------------------

        chat_files = get_chat_files()

        for file in chat_files:

            chat_id = file.replace(".json", "")

            chat_data = load_chat(chat_id)

            if not chat_data:
                continue

            title = chat_data.get(
                "title",
                "New Chat"
            )


            # Current chat indicator

            if chat_id == st.session_state.current_chat_id:

                button_title = "🟢 " + title

            else:

                button_title = "💬 " + title


            col1, col2 = st.columns(
                [5, 1],
                gap="small",
                vertical_alignment="center"
            )


            # -------------------------
            # OPEN CHAT
            # -------------------------

            with col1:

                if st.button(
                    button_title,
                    key=f"chat_{chat_id}",
                    use_container_width=True
                ):

                    selected_chat = load_chat(chat_id)

                    st.session_state.current_chat_id = chat_id

                    st.session_state.messages = (
                        selected_chat.get(
                            "messages",
                            []
                        )
                    )

                    st.session_state.chat_title = (
                        selected_chat.get(
                            "title",
                            "New Chat"
                        )
                    )

                    st.session_state.created_at = (
                        selected_chat.get(
                            "created_at",
                            ""
                        )
                    )

                    st.rerun()


            # -------------------------
            # DELETE CHAT
            # -------------------------

            with col2:

                if st.button(
                    "🗑️",
                    key=f"delete_{chat_id}",
                    use_container_width=True,
                    help="Delete this chat"
                ):

                    delete_chat(chat_id)

                    # Agar current chat delete ho gayi

                    if chat_id == st.session_state.current_chat_id:

                        new_chat_id = create_new_chat()

                        st.session_state.current_chat_id = new_chat_id
                        st.session_state.messages = []
                        st.session_state.chat_title = "New Chat"

                    st.rerun()


        # -----------------------------
        # APP INFO
        # -----------------------------

        st.divider()

        st.caption("🤖 MyOwnAI")
        st.caption("🟢 Local AI")