from transformers import AutoTokenizer, AutoModelForQuestionAnswering, pipeline
import torch
import streamlit as st
from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer

# Initialize Pinecone
pc = Pinecone(api_key='8ec7e752-6ecf-47e4-b8dc-9e6390ae1f28', environment='gcp-starter')

index = pc.Index("qa-index")  # Create an index instance

# Initialize Sentence Transformer
vectorizer = SentenceTransformer('all-MiniLM-L6-v2')

###### Get Answer Function ######
def get_answer(context, question, selected_model):
    if context and question:
        model = AutoModelForQuestionAnswering.from_pretrained(f"{selected_model}")
        tokenizer = AutoTokenizer.from_pretrained(f"{selected_model}")

        nlp = pipeline("question-answering", 
                       model=model, 
                       tokenizer=tokenizer, 
                       device=0 if torch.cuda.is_available() else -1, 
                       framework="pt", 
                       handle_long_generation=True
                      ) 
        QA_input = {
            'question': question,
            'context': context
        }
        answer = nlp(QA_input, handle_impossible_answer=True, top_k=1)
        
        if answer and answer['answer']:
            start_pos = max(0, answer['start'] - 30)  
            end_pos = min(len(context), answer['end'] + 30)  
            surrounding_text = context[start_pos:end_pos]
            return answer, surrounding_text
    return None

#### Display Results Function ####
def display_results(top_answer, question, confidence=None):
    st.subheader(question)
    answer = top_answer['answer']
    if answer.strip():
        st.success(answer)
    else:
        st.error(f'The answer to the question "{question}" cannot be found in the given text.')

    if confidence is not None:
        
        st.text(f"Confidence: {confidence * 100:.0f}%")
        




