import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
import streamlit as st

# Load environment variables from .env file
load_dotenv()

# Function to handle the monthly goals chatbot
def diet(user_data):
    # Get Groq API key from environment
    groq_api_key = os.getenv('GROQ_API_KEY')
    model = 'llama3-8b-8192'

    # Initialize Groq Langchain chat object
    groq_chat = ChatGroq(
        groq_api_key=groq_api_key, 
        model_name=model
    )

    # Define the personalized system prompt for monthly goal setting
    system_prompt = f"""
            You are a Diet planner. The user has the following medical and lifestyle data:
            Based on this data give them personlaized diet. must include --breakfast plan, lunch plan 
            and dinner plan,,-- these three should be header inside each on them give points of what to include ,
            what are necessary and what will be good ,, suggest alernatives also ,,--please display it neatly with good indentaition and neat points
            ,,must include what to take , what to control etc,, do ot start by telling hereis you diet etc etc ,, directly give the headers and points based on user data below
                user-data:
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
            """

    # Get chatbot response directly by sending the system prompt
    response = groq_chat.predict(system_prompt)
    
    # Display chatbot response
    st.write(f"{response}")

if __name__ == "__main__":
    # Example user data to pass to the chatbot
    user_data = {
        "name": "Jane Smith",
        "age": 28,
        "occupation": "Software Engineer",
        "interests": "Programming, Yoga, Reading"
    }

    # Initialize the monthly goals chatbot with user data
    diet(user_data)
