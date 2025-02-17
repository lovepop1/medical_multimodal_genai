import os
import logging
from dotenv import load_dotenv
import streamlit as st
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from datetime import datetime
from groq import Groq

logger=None
groq_client=None

def run_setup():

    logging.basicConfig(level=logging.INFO)
    global logger
    logger = logging.getLogger(__name__)

    # Load environment variables
    load_dotenv()

    # Retrieve API keys from environment variables
    GEMINI_API_KEY = os.getenv('gemini_key')
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")

    # Configure Google Gemini API
    genai.configure(api_key=GEMINI_API_KEY)

    # Initialize the Groq client with the API key
    global groq_client
    groq_client = Groq(api_key=GROQ_API_KEY)

    return [logger, groq_client]

# Define constants for Groq
MODEL_NAME = "llama3-8b-8192"
USER_ROLE = "user"
BOT_ROLE = "mate"

# Define System Prompts and Configurations
system_prompt_image = """ 
As a Highly Skilled medical practitioner specializing in image analysis, you are tasked with examining medical images for a renowned hospital. Your expertise
is crucial in identifying any anomalies, diseases, or health issues that may be present in the images.

Your Responsibilities:
1. Detailed Analysis: Thoroughly analyze each image, focusing on identifying any abnormal findings.
2. Finding reports: Document all observed anomalies or signs of diseases. Clearly articulate these findings in a structured form.
3. Recommendations and Next steps: Based on your analysis, suggest potential next steps, including further tests or treatment as applicable.
4. If appropriate, recommend possible treatment options or interventions.

Important notes:
Scope of response: only respond if the image is related to human health.
Clarity of image: In cases where the image quality impedes clear analysis, note that certain aspects are 'Unable to be determined based on the provided image.' 
"""

generation_config_image = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

generation_config_chat = {
    "temperature": 0.7,
    "top_p": 0.9,
    "max_output_tokens": 1500,
    "response_mime_type": "text/plain",
}


def upload_to_gemini(path, logger, mime_type=None):
    """Uploads the given file to Gemini."""
    try:
        file = genai.upload_file(path, mime_type=mime_type)
        logger.info(f"Uploaded file '{file.display_name}' as: {file.uri}")
        return file
    except Exception as e:
        logger.error(f"Error uploading file to Gemini: {e}")
        return None
    
def analyze_image(image_path, logger):
    """Analyzes the uploaded medical image using Google Gemini API."""
    allowed_extensions = ['.png', '.jpg', '.jpeg', '.webp']
    _, ext = os.path.splitext(image_path)
    if ext.lower() not in allowed_extensions:
        return "Unsupported file type. Please upload a PNG, JPG, JPEG, or WEBP image."

    uploaded_file_info = upload_to_gemini(image_path,logger, mime_type="image/png")
    if not uploaded_file_info:
        return "Failed to upload image for analysis."

    global generation_config_image

    model_image = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config=generation_config_image,
        safety_settings={
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        }
    )

    global system_prompt_image
    chat_session = model_image.start_chat(
        history=[{
            "role": "user",
            "parts": [
                uploaded_file_info,
                system_prompt_image,
            ],
        }]
    )


    try:
        response = chat_session.send_message(system_prompt_image)

        if response.candidates and len(response.candidates) > 0:
            content = response.candidates[0].content.parts[0].text
            return content.strip()
        else:
            return "No analysis results found."
    except Exception as e:
        logger.error(f"Error during image analysis: {e}")
        return f"An error occurred during analysis: {e}"
    
def query_groq_api(user_input, logger):
    """Send the user input to the Groq API and get a response."""
    try:
        logger.info(f"Sending message to Groq API: {user_input}")

        global groq_client
        response = groq_client.chat.completions.create(
            messages=[{
                "role": USER_ROLE,
                "content": user_input,
            }],
            model=MODEL_NAME,
        )

        ai_response = response.choices[0].message.content
        logger.info(f"Received AI response: {ai_response}")

        return ai_response

    except Exception as e:
        logger.error(f"Error when querying Groq API: {e}", exc_info=True)
        return "I'm sorry, I couldn't process that. Please try again."

# run_setup()
# analysis_result=analyze_image(os.path.join('temp_images','temp_img.png'), logger)
# print(analysis_result)

# user_input="I have stomach ache."
# query_response=query_groq_api(user_input, logger)