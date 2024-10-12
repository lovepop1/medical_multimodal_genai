import os
import logging
from dotenv import load_dotenv
import streamlit as st
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from datetime import datetime
from groq import Groq

def app():
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Load environment variables
    load_dotenv()

    # Retrieve API keys from environment variables
    GEMINI_API_KEY = os.getenv('gemini_key')
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")

    if not GEMINI_API_KEY:
        raise ValueError("Google Gemini API key is missing. Please set the 'gemini_key' environment variable.")

    if not GROQ_API_KEY:
        raise ValueError("Groq API key is missing. Please set the 'GROQ_API_KEY' environment variable.")

    # Configure Google Gemini API
    genai.configure(api_key=GEMINI_API_KEY)

    # Initialize the Groq client with the API key
    groq_client = Groq(api_key=GROQ_API_KEY)

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

    def upload_to_gemini(path, mime_type=None):
        """Uploads the given file to Gemini."""
        try:
            file = genai.upload_file(path, mime_type=mime_type)
            logger.info(f"Uploaded file '{file.display_name}' as: {file.uri}")
            return file
        except Exception as e:
            logger.error(f"Error uploading file to Gemini: {e}")
            return None

    def analyze_image(image_path):
        """Analyzes the uploaded medical image using Google Gemini API."""
        allowed_extensions = ['.png', '.jpg', '.jpeg', '.webp']
        _, ext = os.path.splitext(image_path)
        if ext.lower() not in allowed_extensions:
            return "Unsupported file type. Please upload a PNG, JPG, JPEG, or WEBP image."

        uploaded_file_info = upload_to_gemini(image_path, mime_type="image/png")
        if not uploaded_file_info:
            return "Failed to upload image for analysis."

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

    def query_groq_api(user_input):
        """Send the user input to the Groq API and get a response."""
        try:
            logger.info(f"Sending message to Groq API: {user_input}")

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

    def send_chat_message():
        user_input = st.session_state.input_box.strip()
        if user_input:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.session_state.messages.append({
                "role": USER_ROLE,
                "content": user_input,
                "timestamp": timestamp
            })

            with st.spinner("Mate is typing..."):
                bot_response = query_groq_api(user_input)

            bot_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.session_state.messages.append({
                "role": BOT_ROLE,
                "content": bot_response,
                "timestamp": bot_timestamp
            })

            st.session_state.input_box = ""

    def display_chat():
        for message in st.session_state.messages:
            if message["role"] == USER_ROLE:
                st.markdown(
                    f'''
                    <div class="user-message">
                        <strong>You:</strong> {message["content"]}
                        <div class="timestamp">{message["timestamp"]}</div>
                    </div>
                    ''',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f'''
                    <div class="bot-message">
                        <strong>Mate:</strong> {message["content"]}
                        <div class="timestamp">{message["timestamp"]}</div>
                    </div>
                    ''',
                    unsafe_allow_html=True,
                )
        st.markdown('<div id="end"></div>', unsafe_allow_html=True)

    # Streamlit Application
    # st.markdown("<h1>MediMate AI Assistant 🩺</h1>", unsafe_allow_html=True)

    st.title("🩺 MediMate")

    # Initialize session state for chat
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Dropdown selection for mode
    mode = st.selectbox(
        "Select Mode",
        ("Image Analysis", "Chat Bot"),
        index=0,
        key="mode_select",
        label_visibility="hidden"  # Hide the label for a cleaner look
    )

    # ==========================
    # Image Analysis Interface
    # ==========================
    if mode == "Image Analysis":
        st.header("📷 Vital Image Analytics")

        # Instructions
        st.markdown("Upload a medical image to receive a detailed analysis.")

        # File uploader
        uploaded_file = st.file_uploader(
            "Choose an image...",
            type=['png', 'jpg', 'jpeg', 'webp'],
            key="image_upload",
        )

        if uploaded_file is not None:
            # Display the uploaded image in a smaller size
            st.markdown('<div class="image-container">', unsafe_allow_html=True)
            st.image(uploaded_file, caption='Uploaded Image', use_column_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

            # Save the uploaded file to a temporary location
            with st.spinner("Analyzing the image..."):
                try:
                    # Save to a temporary file
                    temp_file_path = os.path.join("temp_images", f"{uploaded_file.name}")
                    os.makedirs("temp_images", exist_ok=True)
                    with open(temp_file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())

                    # Analyze the image
                    analysis_result = analyze_image(temp_file_path)

                    # Remove the temporary file
                    os.remove(temp_file_path)

                    # Display the analysis result
                    st.markdown("### **Analysis Results:**")
                    st.text(analysis_result)

                except Exception as e:
                    logger.error(f"Error during image upload and analysis: {e}")
                    st.error(f"An error occurred: {e}")

    # ==========================
    # Chat Bot Interface
    # ==========================
    elif mode == "Chat Bot":
        st.header("💬 MediMate Chat")

        # Chat container
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        display_chat()
        st.markdown('</div>', unsafe_allow_html=True)

        # Input box and send button aligned horizontally
        st.markdown('<div class="input-container">', unsafe_allow_html=True)
        user_input = st.text_input("You:", placeholder="Type your message here...", key="input_box")
        send_button = st.button("Send", on_click=send_chat_message)
        st.markdown('</div>', unsafe_allow_html=True)

        # Auto-scroll to the latest message
        scroll_js = """
        <script>
        const endElement = document.getElementById('end');
        if (endElement) {
            endElement.scrollIntoView({ behavior: 'smooth' });
        }
        </script>
        """
        st.markdown(scroll_js, unsafe_allow_html=True)

   

