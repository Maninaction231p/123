import streamlit as st
import numpy as np
from PIL import Image
import requests
import random
import time
import google.generativeai as genai

GOOGLE_API_KEY= 'AIzaSyAemx6b6I4EnyMcZI6Bp5Vt0oHdnggbWNo'
genai.configure(api_key=GOOGLE_API_KEY)


st.set_page_config(
    page_title="ChaMage",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
)


st.title("Chat with ChaMage") 


with st.sidebar:
    uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
    image = Image.open(uploaded_file)
    st.image(image, width=275 ,use_container_width =False)


# Choose a Gemini model.
model = genai.GenerativeModel(model_name="gemini-1.5-flash-latest")

# Create a prompt.
prompt = "Give context to the image."
response = model.generate_content([image, prompt])
print(response.text)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": f"{response.text} 👇"}]


# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
    print(st.session_state.messages)

# Create a prompt.
response = model.generate_content([image, prompt])
print(response.text)

prompt = st.chat_input("Type a message...", key="message_input")
# Accept user input
if prompt :
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        # Simulate stream of response with milliseconds delay
        message_placeholder.markdown(response.text)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response.text})

