import streamlit as st
import pandas as pd
import pickle
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from Bio import Entrez, Medline
import os

def app():
    # Set your Entrez email
    Entrez.email = "your.email@example.com"  # **IMPORTANT**: Replace with your actual email

    # Initialize Session State
    if 'articles_df' not in st.session_state:
        st.session_state['articles_df'] = None
    if 'embeddings' not in st.session_state:
        st.session_state['embeddings'] = None
    if 'faiss_index' not in st.session_state:
        st.session_state['faiss_index'] = None
    if 'recommendations' not in st.session_state:
        st.session_state['recommendations'] = None

    # Load or build FAISS index function
    def build_faiss_index(embeddings):
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatIP(dimension)  # Using Inner Product for cosine similarity
        faiss.normalize_L2(embeddings)
        index.add(embeddings)
        return index

    # Save FAISS index and embeddings
    def save_faiss_index(embeddings, index, embedding_path, index_path):
        with open(embedding_path, 'wb') as f:
            pickle.dump(embeddings, f)
        faiss.write_index(index, index_path)

    # Load FAISS index and embeddings
    def load_faiss_index(embedding_path, index_path):
        if os.path.exists(index_path) and os.path.exists(embedding_path):
            with open(embedding_path, 'rb') as f:
                embeddings = pickle.load(f)
            index = faiss.read_index(index_path)
            return index, embeddings
        else:
            return None, None

    # Fetch PubMed articles
    def fetch_pubmed(query, max_results=100):
        try:
            handle = Entrez.esearch(db="pubmed", term=query, retmax=max_results)
            record = Entrez.read(handle)
            handle.close()

            id_list = record.get("IdList", [])

            if not id_list:
                st.warning("No articles found for the given query.")
                return pd.DataFrame()  # Return empty DataFrame if no IDs found

            handle = Entrez.efetch(db="pubmed", id=id_list, rettype="medline", retmode="text")
            records = Medline.parse(handle)
            records = list(records)
            handle.close()

            articles = []
            for record in records:
                article = {
                    "PMID": record.get("PMID", ""),
                    "Title": record.get("TI", ""),
                    "Abstract": record.get("AB", ""),
                    "Authors": ", ".join(record.get("AU", [])),
                    "Journal": record.get("JT", ""),
                    "Publication Year": record.get("DP", "").split()[0] if record.get("DP", "") else ""
                }
                articles.append(article)

            return pd.DataFrame(articles)

        except Exception as e:
            st.error(f"An error occurred while fetching PubMed articles: {e}")
            return pd.DataFrame()

    # Encode abstracts
    @st.cache_resource  # Cache the model to avoid reloading
    def load_model():
        try:
            model = SentenceTransformer('all-MiniLM-L6-v2')
            return model
        except Exception as e:
            st.error(f"Error loading SentenceTransformer model: {e}")
            return None

    def encode_abstracts(abstracts, model):
        try:
            embeddings = model.encode(abstracts, show_progress_bar=True)
            return embeddings.astype('float32')  # Ensure float32 for FAISS
        except Exception as e:
            st.error(f"Error encoding abstracts: {e}")
            return None

    # Recommend papers based on similarity
    def recommend_papers(query_embedding, index, df, top_k=5):
        try:
            # Normalize the query embedding (for cosine similarity)
            query_embedding = query_embedding.reshape(1, -1)
            faiss.normalize_L2(query_embedding)

            # Search the index for the top_k most similar articles
            D, I = index.search(query_embedding, top_k)

            # Retrieve the top_k articles
            recommendations = df.iloc[I[0]].copy()
            recommendations['Score'] = D[0]
            return recommendations
        except Exception as e:
            st.error(f"Error during recommendation: {e}")
            return pd.DataFrame()

    # Load the SentenceTransformer model
    model = load_model()
    if model is None:
        st.stop()  # Stop the app if the model failed to load

    st.title("PubMed Research Paper Recommender")

    st.write("""
    This app recommends PubMed research papers based on abstract similarity and not just keyword matching using FAISS indexing and Sentence-BERT embeddings.
    Follow these steps:
    1. **Enter a PubMed search query** and fetch relevant articles.
    2. **Build the FAISS index** from the fetched articles.
    3. **Recommend similar papers** based on a new query.
    """)

    # Step 1: Fetch Articles
    query = st.text_input("Enter a PubMed search query", "")
    num_results = st.slider("Number of articles to fetch", min_value=10, max_value=200, value=50)

    if st.button("Fetch Articles"):
        if query.strip() == "":
            st.error("Please enter a non-empty search query.")
        else:
            with st.spinner("Fetching articles from PubMed..."):
                articles_df = fetch_pubmed(query, num_results)
                if articles_df.empty:
                    st.warning("No articles fetched.")
                else:
                    st.success(f"Fetched {len(articles_df)} articles.")
                    st.session_state['articles_df'] = articles_df
                    st.dataframe(articles_df[['Title', 'Abstract', 'Authors', 'Journal', 'Publication Year']])

    # # Display fetched articles if available
    # if st.session_state['articles_df'] is not None:
    #     st.write("### Fetched Articles")
    #     st.dataframe(st.session_state['articles_df'][['Title', 'Abstract', 'Authors', 'Journal', 'Publication Year']])

    st.write("---")

    # Step 2: Build FAISS Index
    st.subheader("Build FAISS(Facebook AI Similarity Search) Index")
    embedding_path = "pubmed_recommender/embeddings.pkl"  # You can customize the path
    index_path = "pubmed_recommender/faiss_index.index"   # You can customize the path

    if st.button("Build FAISS Index"):
        if st.session_state['articles_df'] is None:
            st.error("Please fetch articles first before building the FAISS index.")
        else:
            with st.spinner("Encoding abstracts and building FAISS index..."):
                abstracts = st.session_state['articles_df']['Abstract'].tolist()
                if not abstracts or all(not ab for ab in abstracts):
                    st.error("No abstracts available to encode.")
                else:
                    embeddings = encode_abstracts(abstracts, model)
                    if embeddings is not None:
                        index = build_faiss_index(embeddings)
                        save_faiss_index(embeddings, index, embedding_path, index_path)
                        st.session_state['embeddings'] = embeddings
                        st.session_state['faiss_index'] = index
                        st.success("FAISS index built and saved successfully.")

    # Check if FAISS index is already loaded or can be loaded
    if st.session_state['faiss_index'] is None:
        index, embeddings = load_faiss_index(embedding_path, index_path)
        if index is not None and embeddings is not None:
            st.session_state['faiss_index'] = index
            st.session_state['embeddings'] = embeddings
            st.success("Loaded existing FAISS index and embeddings.")
        else:
            st.info("FAISS index and embeddings not found. Please build the index.")

    st.write("---")

    # Step 3: Recommend Papers
    st.subheader("Recommend Similar Papers")
    recommendation_query = st.text_input("Enter a query to get recommendations", "")

    if st.button("Recommend Papers"):
        if recommendation_query.strip() == "":
            st.error("Please enter a non-empty query for recommendations.")
        elif st.session_state['faiss_index'] is None or st.session_state['embeddings'] is None:
            st.error("FAISS index not available. Please build the index first.")
        else:
            with st.spinner("Encoding query and searching for similar papers..."):
                query_embedding = encode_abstracts([recommendation_query], model)
                if query_embedding is not None:
                    query_embedding = query_embedding[0]
                    recommendations = recommend_papers(query_embedding, st.session_state['faiss_index'], st.session_state['articles_df'], top_k=5)
                    if not recommendations.empty:
                        st.success("Top 5 Recommendations:")
                        st.dataframe(recommendations[['Title', 'Abstract', 'Authors', 'Journal', 'Publication Year', 'Score']])
                        st.session_state['recommendations'] = recommendations
                    else:
                        st.warning("No recommendations found.")
                        
                else:
                    st.error("Failed to encode the recommendation query.")

    # # Display recommendations if available
    # if st.session_state['recommendations'] is not None:
    #     st.write("### Recommendations")
    #     st.dataframe(st.session_state['recommendations'][['Title', 'Abstract', 'Authors', 'Journal', 'Publication Year', 'Score']])

# if __name__ == "__main__":
#     app()
