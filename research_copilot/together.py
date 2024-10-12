import streamlit as st
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from concurrent.futures import ThreadPoolExecutor
from transformers import T5Tokenizer, T5ForConditionalGeneration, pipeline
import base64
import torch
import os
import io
import time
from research_copilot import document_uploader
from research_copilot import qa_system

def app():
    # Fixed model name for question answering
    FIXED_MODEL_NAME = "bert-large-uncased-whole-word-masking-finetuned-squad"

    # Model and tokenizer for summarization
    model_checkpoint = "MBZUAI/LaMini-Flan-T5-248M"
    model_tokenizer = T5Tokenizer.from_pretrained(model_checkpoint, legacy=False)
    model = T5ForConditionalGeneration.from_pretrained(model_checkpoint, device_map='auto', torch_dtype=torch.float32)

    summarization_pipeline = pipeline(
        'summarization',
        model=model,
        tokenizer=model_tokenizer,
        max_length=500,
        min_length=70
    )

    # Function to preprocess and split PDF into chunks
    def preprocess_pdf(file):
        loader = PyPDFLoader(file)
        pages = loader.load_and_split()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1700, chunk_overlap=70)
        texts = text_splitter.split_documents(pages)
        return texts

    # Summarization logic
    def summarize_chunk(chunk, max_length):
        input_length = len(chunk.page_content.split())
        dynamic_max_length = min(max_length, input_length // 3)
        dynamic_min_length = max(dynamic_max_length // 2, 30)

        try:
            return summarization_pipeline(chunk.page_content, max_length=dynamic_max_length, min_length=dynamic_min_length)[0]['summary_text']
        except Exception as e:
            st.error(f"Error during summarization: {e}")
            return ""

    def language_model_pipeline(filepath, max_length):
        chunks = preprocess_pdf(filepath)

        with ThreadPoolExecutor() as executor:
            results = list(executor.map(lambda chunk: summarize_chunk(chunk, max_length), chunks))

        combined_summaries = " ".join(filter(None, results))
        final_summary = summarization_pipeline(combined_summaries, max_length=max_length, min_length=max_length // 2)
        return final_summary[0]['summary_text']

    # Function to display the PDF content
    # @st.cache_data
    def display_pdf(file):
        with open(file, "rb") as f:
            base64_pdf = base64.b64encode(f.read()).decode('utf-8')

        pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600" type="application/pdf"></iframe>'
        st.markdown(pdf_display, unsafe_allow_html=True)
        # st.download_button(label="Download PDF", data=f.read(), file_name=file)
        # with open(file, "rb") as f:
            

    # Session state
    if 'context' not in st.session_state:
        st.session_state.context = ""
    if 'uploaded_file_path' not in st.session_state:
        st.session_state['uploaded_file_path'] = None

    # Sidebar section

    st.title("Research Copilot")
    st.write("Your Complete Guide to Medical Research")
    
    st.write("Upload Research paper(PDF) to summarize or ask questions.")
    uploaded_file = st.file_uploader("Upload your PDF file", type=['pdf'])

        # If a file is uploaded, store the path
    if uploaded_file:
        if not os.path.exists('research_copilot\pdf'):
            os.makedirs('research_copilot\pdf')
        filepath = os.path.join('research_copilot\pdf', uploaded_file.name)
        with open(filepath, "wb") as temp_file:
            temp_file.write(uploaded_file.read())
        st.session_state.uploaded_file_path = filepath

    # Display uploaded PDF and options to either summarize or ask questions
    if st.session_state.uploaded_file_path:
        display_pdf(st.session_state.uploaded_file_path)

        tab1, tab2 = st.tabs(["Summarize", "Ask Questions"])

        # Summarization tab
        with tab1:
            st.header("Summarization")
            max_len = st.number_input("Enter maximum length for summary", min_value=50, max_value=1000, value=500, step=50)
            if st.button("Summarize"):
                st.write("Might take a few minutes. Please wait ....")
                summarized_result = language_model_pipeline(st.session_state.uploaded_file_path, max_len)
                st.success("Summarization Complete")
                st.text_area("Summarized Text", summarized_result, height=300)

        # Question Answering tab
        with tab2:
            st.header("Question Answering")
            question = st.text_input("Ask a question about the document")
            if st.button("Submit Question"):
                if not question:
                    st.warning("Ask a question first...")
                else:
                    st.write("Might take a few minutes. Please wait ....")
                    try:
                        # Extract the text from the uploaded PDF for question answering
                        chunks = preprocess_pdf(st.session_state.uploaded_file_path)
                        document_text = " ".join([chunk.page_content for chunk in chunks])  # Combine all chunks into a single string

                        start_time = time.time()
                        with st.spinner("Processing..."):
                            # Pass the extracted text as a string to the get_answer function
                            result = qa_system.get_answer(document_text, question, FIXED_MODEL_NAME)
                            if result:
                                original_answer, search_term = result
                                qa_system.display_results(original_answer, question)

                                # Highlighting in the PDF
                                with st.expander("View Evidence"):
                                    images = document_uploader.get_highlighted_image(st.session_state.uploaded_file_path, str(search_term), original_answer['answer'].strip())
                                    for img, page_number in images:
                                        img_byte_arr = io.BytesIO()
                                        img.save(img_byte_arr, format='PNG')
                                        st.image(img_byte_arr.getvalue(), caption=f'Highlighted Page (Page {page_number})', use_column_width=True)

                        end_time = time.time()
                        st.markdown(f"Query processed in {end_time - start_time:.2f} seconds")

                    except Exception as e:
                        st.error(f"An error occurred: {e}")

# # Run the app function if called from the main module
# if __name__ == "__main__":
#     app()
