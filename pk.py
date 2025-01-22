import streamlit as st
import numpy as np
from PIL import Image
import requests
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


with st.expander('See Details',expanded=True):
    st.title("Upload Image") 
    st.markdown("To Unleash your creativity with Chamage, the innovative image-based chatbot. Share your favorite images, and Chamage will use them as inspiration to craft unique and imaginative responses. Explore new ideas, spark your creativity, and have fun conversing with Chamage!")


with st.sidebar:
    uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, width=275 ,use_container_width =False)

if uploaded_file:
    st.markdown("##Chat with ChaMage") 


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
            print(prompt)
            response1 = model.generate_content([image, prompt])

            # Simulate stream of response with milliseconds delay
            message_placeholder.markdown(response1.text)
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response1.text})

