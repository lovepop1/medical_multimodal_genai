# Gen AI-Powered Medical Research, Treatment, and Diagnosis App

This application is designed to assist with medical research, treatment, and diagnosis, using state-of-the-art AI technologies integrated with Streamlit.

## Prerequisites

- Python version 3.12
  - Download and install Python 3.12 from the official website: [Python Downloads](https://www.python.org/downloads/)
  
- A `groq` API key from [Groq Console](https://console.groq.com/keys)
- A `gemini` API key from [Google AI Studio](https://aistudio.google.com/app/apikey)

## Project Setup

### Step 1: Clone or download the project files

Ensure that you have the following files in your project directory:
- `main.py`
- `requirements.txt`

### Step 2: Set up Python Virtual Environment

1. Navigate to the project directory.
2. Run the following command to create a virtual environment:

for Windows Powershell:
   1) python -m venv .venv 
   2) .venv\Scripts\Activate.ps1

### Step 3: Install all requirements

1. Navigate to the project directory.
2. Run the following command to create a virtual environment:

for Windows Powershell:
   1) pip install -r requirements.txt

### Step 4: Enter your api keys in these .env files with no quotes

1. multimodal_diagnosis\.env
2. data_synthesis_and_personalized_treatment\.env

### Step 5: Run ypur app

1. Navigate to the project directory.
2. Run the following command to create a virtual environment:

for Windows Powershell:
   1) streamlit run .\main.py



