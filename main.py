import streamlit as st
import os
import subprocess
import os
import logging
from dotenv import load_dotenv
import streamlit as st
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from datetime import datetime
from groq import Groq
import multimodal_diagnosis.diagnosis
import personalized_treatment.app
import data_synthesis_and_personalized_treatment.general_ehr_generator
import data_quality_check.testing_synthetic_data
import drug_discovery.test
import research_copilot.together
import pubmed_recommender.recommender
import webbrowser
import requests

# Apply a global style template with the requested customizations




def template1_page_style():
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Kode+Mono:wght@400..700&family=Smooch+Sans:wght@100..900&display=swap');
            .stApp {
                background: linear-gradient(to bottom, #010110, #14062E, #422989, #A951D2, #DF84E1, #FCA5FE);
                color: white;  
                font-family: 'Kode Mono', sans-serif;
            }
            h1 {
                font-size: 55px;
                font-family: 'Kode Mono', sans-serif;
                color: white !important;
                text-align: left;
                background: none;
            }
            h1 + p {
                font-size: 24px;
                color: white;
                text-align: center;
                margin-top: 10px;
                font-family: 'Kode Mono', sans-serif;
            }
            [data-testid="stSidebar"] {
                background-color: #000000;
                color: white;
                font-family: 'Kode Mono', sans-serif;
            }
            .stButton button {
                background-color: #6C3483;
                color: white !important;
                font-family: 'Kode Mono', sans-serif !important;
                font-size: 18px !important;
                border-radius: 8px;
                padding: 10px 20px;
                margin-bottom: 10px;
                width: 100%;
                border: none;
                transition: all 0.3s ease;
            }
            .stButton button:hover {
                background-color: #884EA0;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
                transform: translateY(-2px);
            }
                
            .stDownloadButton button {
                background-color: #6C3483;
                color: white !important;
                font-family: 'Kode Mono', sans-serif !important;
                font-size: 18px !important;
                border-radius: 8px;
                padding: 10px 20px;
                margin-bottom: 10px;
                width: 100%;
                border: none;
                transition: all 0.3s ease;
            }

            .stDownloadButton button:hover {
                background-color: #884EA0;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
                transform: translateY(-2px);
            }
            .stHeader{
                color: white !important;
            }
            input, select, textarea {
                border-radius: 8px;
                border: 1px solid #ddd;
                padding: 12px;
                font-size: 16px;
                font-family: 'Kode Mono', sans-serif;
                margin-bottom: 20px;
                width: 100%;
            }
            input:focus, select:focus, textarea:focus {
                border-color: #6C3483;
                box-shadow: 0 0 8px rgba(108, 52, 131, 0.4);
                outline: none;
            }
            header[data-testid="stHeader"] {
                background-color: rgba(0, 0, 0, 0);
                font-size: 60px;
                font-family: 'Kode Mono', sans-serif;
                color: white !important;
                text-align: left;
                background: none;

            }
            footer {
                background-color: rgba(0, 0, 0, 0);
            }
        </style>
    """, unsafe_allow_html=True)

def sidebar_navigation():
    # Use session state to remember the current page
    if "current_page" not in st.session_state:
        st.session_state.current_page = "Home"
    
    # Sidebar navigation buttons
    if st.sidebar.button("HOME \u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0🏠"):
        st.session_state.current_page = 'Home'
    if st.sidebar.button("AI MULTIMODAL DIAGNOSIS \u00A0\u00A0\u00A0\u00A0\u00A0🩺"):
        st.session_state.current_page = 'Diagnosis'
    if st.sidebar.button("PERSONALIZED TREATMENT \u00A0\u00A0\u00A0\u00A0⚕️"):
        st.session_state.current_page = 'Personalized Treatment'
    if st.sidebar.button("HEALTH RECORDS SYNTHESIS \u00A0📄"):
        st.session_state.current_page = 'Health Records'
    if st.sidebar.button("LITERATURE RECOMMENDER \u00A0\u00A0\u00A0\u00A0🔍"):
        st.session_state.current_page = 'Literature Review'
    if st.sidebar.button("RESEARCH COPILOT \u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0🧬"):
        st.session_state.current_page = 'Research Copilot'
    if st.sidebar.button("HEALTH IMAGE SYNTHESIS \u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0🖼️"):
        st.session_state.current_page = 'Health Image'
    if st.sidebar.button("SYNTHETIC QUALITY CHECK \u00A0\u00A0\u00A0\u00A0\u00A0\u00A0✅"):
        st.session_state.current_page = 'Quality Check'
    if st.sidebar.button("DRUG DISCOVERY \u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0💊"):
        st.session_state.current_page = 'Drug Discovery'

# Main Home page content
def show_home():
    st.markdown("""
        <div style="text-align: center; margin-top: 10px;">
            <h1>
                Gen Ai Medical Diagnosis, Treatment and Research Copilot
            </h1>
            <p style="font-size: 24px; color: white; margin-top: 10px; font-family: 'Kode Mono', sans-serif; text-align:left;">
                Empowering medical diagnosis and research with AI-driven insights and diagnostics.
            </p>
        </div>
    """, unsafe_allow_html=True)

    
# Other pages as placeholders
def show_literature_recommender():
    pubmed_recommender.recommender.app()

def show_personalized_treatment():
    personalized_treatment.app.app()

def show_record_synthesis():
    data_synthesis_and_personalized_treatment.general_ehr_generator.app()

def show_research_copilot():
    research_copilot.together.app()

def show_diagnosis():
    multimodal_diagnosis.diagnosis.app()
    
def show_data_quality():
    data_quality_check.testing_synthetic_data.app()

def show_drug_discovery():
    drug_discovery.test.app()


def show_image_synthesis():
    st.title('Health Image Synthesis')
    st.write("Please run the Colab file and open the Gradio link generated after running the code.")
    
    if st.button("Open Colab File"):
        webbrowser.open_new_tab("https://colab.research.google.com/drive/18u8LXnXDxkscEfcYl3POFRYZh7mj-NJf?usp=sharing")
# Main function
def main():
    # Apply page styles
    template1_page_style()
    
    # Sidebar navigation
    sidebar_navigation()
    
    # Display the page according to the session state
    if st.session_state.current_page == 'Home':
        show_home()
    elif st.session_state.current_page == 'Literature Review':
        show_literature_recommender()
    elif st.session_state.current_page == 'Personalized Treatment':
        show_personalized_treatment()
    elif st.session_state.current_page == 'Health Records':
        show_record_synthesis()
    elif st.session_state.current_page == 'Research Copilot':
        show_research_copilot()
    elif st.session_state.current_page == 'Diagnosis':
        show_diagnosis()
    elif st.session_state.current_page == 'Health Image':
        show_image_synthesis()
    elif st.session_state.current_page == 'Quality Check':
        show_data_quality()
    elif st.session_state.current_page == 'Drug Discovery':
        show_drug_discovery()

if __name__ == "__main__":  
    main()
