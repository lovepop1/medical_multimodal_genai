import os
import base64
from dotenv import load_dotenv
import streamlit as st
from groq import Groq
from langchain.chains import LLMChain
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain_core.messages import SystemMessage
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain_groq import ChatGroq
import requests

# Load the .env file for the API key
load_dotenv()

def app():
    # Initialize the Groq client with the API key
    client = Groq(
        api_key=os.environ.get("GROQ_API_KEY"),
    )

    # Function to encode the image to base64 for local files
    def encode_image(image_path):
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except FileNotFoundError:
            return None

    # Function to validate the URL
    def validate_url(image_url):
        try:
            response = requests.head(image_url)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False

    # Function to handle medical-specific chat interactions with memory
    def chat_with_memory(model, memory, user_input, image_path=None, image_url=None):
        # Construct the system prompt to focus on medical conversations
        system_prompt = (
            'You are a medical assistant chatbot. Only answer medical-related questions '
            'and neglect non-medical ones. If the user asks non-medical questions, respond '
            'with: "I can only assist with medical questions." '
            'For medical questions, provide personalized suggestions, including '
            'possible diagnoses, treatments, exercises, and dietary advice.'
        )

        # Construct a chat prompt template using various components
        prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessage(content=system_prompt),  # System prompt for medical-only behavior
                MessagesPlaceholder(variable_name="chat_history"),  # Placeholder for chat history
                HumanMessagePromptTemplate.from_template("{human_input}"),  # User input template
            ]
        )

        # Create a conversation chain using the LLM (Language Learning Model)
        conversation = LLMChain(
            llm=model,  # The Groq LangChain chat object initialized earlier
            prompt=prompt,  # The constructed prompt template
            verbose=False,  # Enables verbose output for debugging
            memory=memory,  # The conversational memory object to store chat history
        )

        # Handle text-only conversations
        if image_path is None and image_url is None:
            response = conversation.predict(human_input=user_input)

        # Handle local image input
        elif image_path is not None:
            base64_image = encode_image(image_path)
            if base64_image is None:
                return "Invalid local image path. Please try again."
            response = conversation.predict(human_input=f"{user_input} with image data {base64_image}")

        # Handle image URL input
        elif image_url is not None:
            if not validate_url(image_url):
                return "Invalid image URL. Please check the URL and try again."
            response = conversation.predict(human_input=f"{user_input} with image at {image_url}")

        return response

    # Main Streamlit app
    st.title("Personalized Medical Treatment")
    st.write("Feel free to state your medical symptoms here and get treatment plans")

    # Initialize conversational memory (stores last 5 interactions)
    conversational_memory_length = 5
    memory = ConversationBufferWindowMemory(k=conversational_memory_length, memory_key="chat_history", return_messages=True)

    # Collect user input
    user_input = st.text_input("You: ", placeholder="Enter your symptoms..")

    # Select the image option
    image_option = st.radio("Would you like to provide an image?", options=("No Image", "Local Image", "Image URL"))

    # Variables to store image paths or URLs
    image_path = None
    image_url = None

    # Handling image option
    if image_option == "Local Image":
        image_path = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
        if image_path:
            image_path = image_path.name
    elif image_option == "Image URL":
        image_url = st.text_input("Enter the image URL:")

    # Create a button to submit the query
    if st.button("Submit"):
        # Basic personalized interaction model
        if image_option == "No Image":
            response = chat_with_memory(
                model=ChatGroq(groq_api_key=os.environ['GROQ_API_KEY'], model_name='llama3-8b-8192'),
                memory=memory,
                user_input=user_input,
            )
        elif image_option == "Local Image" and image_path:
            response = chat_with_memory(
                model=ChatGroq(groq_api_key=os.environ['GROQ_API_KEY'], model_name='llama-3.2-11b-vision-preview'),
                memory=memory,
                user_input=user_input,
                image_path=image_path,
            )
        elif image_option == "Image URL" and image_url:
            response = chat_with_memory(
                model=ChatGroq(groq_api_key=os.environ['GROQ_API_KEY'], model_name='llama-3.2-11b-vision-preview'),
                memory=memory,
                user_input=user_input,
                image_url=image_url,
            )
        else:
            st.error("Invalid input or missing image. Please try again.")

        # Display the response with enhanced formatting
        if response:
            st.markdown(f"Response:")
            st.write(response)

# In main.py, you can now call `app()` to run this bot
