import os
import streamlit as st
from groq import Groq
from dotenv import load_dotenv
import logging

for name in list(logging.root.manager.loggerDict):
    if name.startswith("streamlit"):
        logging.getLogger(name).setLevel(logging.ERROR)

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY") or st.secrets["GROQ_API_KEY"]
client = Groq(api_key=GROQ_API_KEY)

st.set_page_config(page_title="puli Chatbot", layout="centered")
st.title("💬 Puli Chatbot")

if "history" not in st.session_state:
    st.session_state.history = [
        {"role": "system", "content": "You are a helpful assistant."}
    ]
if "model" not in st.session_state:
    st.session_state.model = "meta-llama/llama-4-scout-17b-16e-instruct"

with st.sidebar:
    st.header("Settings")
    st.session_state.model = st.selectbox(
        "Model",
        [
            "meta-llama/llama-4-scout-17b-16e-instruct",
            "mixtral-8x7b-32768"
        ]
    )
    if st.button("Clear chat"):
        st.session_state.history = [
            {"role": "system", "content": "You are a helpful assistant."}
        ]

def stream_response(user_input: str):
    st.session_state.history.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    response_stream = client.chat.completions.create(
        model=st.session_state.model,
        messages=st.session_state.history,
        temperature=1,
        stream=True,
    )

    buffer = ""
    placeholder = st.empty()
    with st.chat_message("assistant"):
        for chunk in response_stream:
            delta = chunk.choices[0].delta.content or ""
            buffer += delta
            if buffer.endswith(('.', '!\n', '\n\n')):
                placeholder.write(buffer)
        placeholder.write(buffer)

    st.session_state.history.append({"role": "assistant", "content": buffer})
if user := st.chat_input("Type your message..."):
    stream_response(user)
