import streamlit as st
import webbrowser
import threading

def open_browser():
    """Open the Streamlit app in a web browser."""
    webbrowser.open("https://9fe16485f1504e0ee8.gradio.live")

def app():
    """Run the Streamlit app and open it in a browser."""
    # Start the Streamlit app in a separate thread
    threading.Thread(target=open_browser).start()
    

if __name__ == "__main__":
    app()