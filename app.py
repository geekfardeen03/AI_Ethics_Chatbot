import streamlit as st
import json
import os
import google.generativeai as genai

# -------------------------------
# CONFIG
# -------------------------------
st.set_page_config(page_title="AI Ethics Chatbot", layout="wide")

DATA_FILE = "users.json"
GEMINI_API_KEY = os.getenv("AIzaSyA-JKYNIODPguOaKz9HkFBcMh6oANpr32s") 

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-pro")


# -------------------------------
# DATA HANDLING
# -------------------------------
def load_users():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_users(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)


# -------------------------------
# AUTH
# -------------------------------
def create_user(username, password):
    users = load_users()
    if username in users:
        return False

    users[username] = {
        "password": password,
        "chats": {}
    }

    save_users(users)
    return True


def authenticate(username, password):
    users = load_users()
    return username in users and users[username]["password"] == password


def get_user_data(username):
    users = load_users()
    return users.get(username, {})


# -------------------------------
# AI LOGIC
# -------------------------------
def detect_domain(query):
    query = query.lower()

    if "hospital" in query or "patient" in query:
        return "Healthcare"
    elif "loan" in query or "bank" in query:
        return "Finance"
    elif "hiring" in query or "job" in query:
        return "Recruitment"
    else:
        return "General"


def generate_response(query):
    domain = detect_domain(query)

    prompt = f"""
You are an AI Ethics Assistant.

User Query: {query}
Domain: {domain}

Respond in this format:

Answer:
Explanation:
Ethical Principle:

Keep response clear and professional.
"""

    response = model.generate_content(prompt)
    return response.text


def generate_chat_title(first_message):
    prompt = f"Give a short 3-5 word title for: {first_message}"
    try:
        res = model.generate_content(prompt)
        return res.text.strip().replace("\n", "")
    except:
        return "New Chat"


# -------------------------------
# CHAT STORAGE
# -------------------------------
def save_chat(username, chat_id, messages):
    users = load_users()
    users[username]["chats"][chat_id]["messages"] = messages
    save_users(users)


def create_new_chat(username, first_prompt):
    users = load_users()
    chats = users[username].get("chats", {})

    chat_id = f"chat_{len(chats)+1}"
    title = generate_chat_title(first_prompt)

    chats[chat_id] = {
        "title": title,
        "messages": []
    }

    users[username]["chats"] = chats
    save_users(users)

    return chat_id


# -------------------------------
# SESSION STATE
# -------------------------------
if "user" not in st.session_state:
    st.session_state.user = None

if "current_chat" not in st.session_state:
    st.session_state.current_chat = None

if "messages" not in st.session_state:
    st.session_state.messages = []


# -------------------------------
# AUTH UI
# -------------------------------
def show_auth():
    st.markdown("<h2 style='text-align:center;'>AI Ethics Chatbot</h2>", unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["Login", "Signup"])

    with tab1:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if authenticate(username, password):
                st.session_state.user = username
                st.rerun()
            else:
                st.error("Invalid credentials")

    with tab2:
        username = st.text_input("New Username")
        password = st.text_input("New Password", type="password")

        if st.button("Create Account"):
            if create_user(username, password):
                st.success("Account created. Please login.")
            else:
                st.error("Username already exists")


# -------------------------------
# SIDEBAR
# -------------------------------
def sidebar():
    user = st.session_state.user
    data = get_user_data(user)
    chats = data.get("chats", {})

    st.sidebar.markdown(f"### 👤 {user}")

    if st.sidebar.button("➕ New Chat"):
        st.session_state.current_chat = None
        st.session_state.messages = []

    if st.sidebar.button("🚪 Logout"):
        st.session_state.user = None
        st.session_state.current_chat = None
        st.session_state.messages = []
        st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.markdown("### Chats")

    for chat_id, chat_data in chats.items():
        title = chat_data.get("title", chat_id)

        if st.sidebar.button(title):
            st.session_state.current_chat = chat_id
            st.session_state.messages = chat_data["messages"]


# -------------------------------
# PROCESS INPUT
# -------------------------------
def handle_user_input(prompt):
    user = st.session_state.user

    if not st.session_state.current_chat:
        chat_id = create_new_chat(user, prompt)
        st.session_state.current_chat = chat_id

    chat_id = st.session_state.current_chat

    st.session_state.messages.append(("user", prompt))

    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_text = ""

        response = generate_response(prompt)

        for word in response.split():
            full_text += word + " "
            placeholder.markdown(full_text)

    st.session_state.messages.append(("assistant", full_text))

    save_chat(user, chat_id, st.session_state.messages)

    st.rerun()


# -------------------------------
# LANDING SCREEN
# -------------------------------
def landing():
    st.markdown(
        "<h1 style='text-align:center; margin-top:120px;'>What shall we think through?</h1>",
        unsafe_allow_html=True
    )

    prompt = st.chat_input("Ask about AI ethics...")

    if prompt:
        handle_user_input(prompt)


# -------------------------------
# CHAT UI
# -------------------------------
def chat_ui():
    for role, msg in st.session_state.messages:
        st.chat_message(role).markdown(msg)

    prompt = st.chat_input("Type your message...")

    if prompt:
        handle_user_input(prompt)


# -------------------------------
# MAIN
# -------------------------------
if not st.session_state.user:
    show_auth()
else:
    sidebar()

    if not st.session_state.messages:
        landing()
    else:
        chat_ui()