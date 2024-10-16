import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
import streamlit as st

# Load environment variables from .env file
load_dotenv()

# Function to handle the medical chatbot
def medical_chatbot(user_data):
    # Get Groq API key from environment
    groq_api_key = os.getenv('GROQ_API_KEY')
    model = 'llama3-8b-8192'

    # Initialize Groq Langchain chat object
    groq_chat = ChatGroq(
        groq_api_key=groq_api_key, 
        model_name=model
    )

    # Define the personalized system prompt for the chatbot
    system_prompt = f"""
    You are a helpful medical assistant. The user has the following medical data:
    - Name: {user_data.get('name', 'Unknown')}
            - Age: {user_data.get('age', 'Unknown')}
            - Gender: {user_data.get('gender', 'Unknown')}
            - Height: {user_data.get('height', 'Unknown')} cm
            - Weight: {user_data.get('weight', 'Unknown')} kg
            - BMI: {user_data.get('bmi', 'Unknown')}
            - Known Allergies: {user_data.get('allergies', 'None')}
            - Current Medications: {user_data.get('current_medications', 'None')}
            - Previous Medical Conditions: {user_data.get('previous_conditions', 'None')}
            - Previous Medications: {user_data.get('previous_medications', 'None')}
            - Doctors Visited: {user_data.get('visited_doctors', 'None')}
            - Smoking Habits: {user_data.get('smoking_habits', 'Unknown')}
            - Drinking Habits: {user_data.get('drinking_habits', 'Unknown')}
            - Exercise Frequency: {user_data.get('exercise_frequency', 'Unknown')}
            - Average Sleep Duration: {user_data.get('sleep_duration', 'Unknown')} hours per night
            - Current Diet: {user_data.get('current_diet', 'Unknown')}
            - Family Medical History: {user_data.get('family_medical_history', 'None')}
    
    The user will describe a symptom or issue they are experiencing. Provide personalized health advice, assess the seriousness of the issue and mention it to the user, suggest possible treatment plans, and recommend immediate actions if necessary. Offer additional health recommendations. Do not give solutions to non-medical questions.
    """

    # Streamlit interface for the chatbot
    st.write("Enter your symptoms or health-related question to receive personalized advice.")

    # Input from the user
    user_input = st.text_input("Describe your symptoms or ask a health-related question:")

    # Ensure chat history is initialized
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []

    if st.button("Get Response"):
        if user_input:
            # Append system prompt and user input
            full_prompt = system_prompt + "\nUser's input: " + user_input

            # Get chatbot response directly by sending the full prompt
            response = groq_chat.predict(full_prompt)
            
            # Display chatbot response
            st.write(f"**Chatbot Response:** {response}")

            # Update chat history with new message and response
            st.session_state["chat_history"].append({"role": "user", "content": user_input})
            st.session_state["chat_history"].append({"role": "assistant", "content": response})
        else:
            st.warning("Please enter a symptom or question.")

if __name__ == "__main__":
    # Example user data to pass to the chatbot
    user_data = {
        "name": "John Doe",
        "age": 30,
        "bmi": 24.5,
        "allergies": "None",
        "current_medications": "None",
        "previous_conditions": "Hypertension"
    }

    # Initialize the chatbot with user data
    medical_chatbot(user_data)
