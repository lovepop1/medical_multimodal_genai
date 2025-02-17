import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
import numpy as np
import pickle
import os
import faiss
# from recommender import fetch_pubmed, encode_abstracts, build_faiss_index, save_faiss_index, load_faiss_index, recommend_papers
from recommender import app
from sentence_transformers import SentenceTransformer

class TestPubMedRecommender(unittest.TestCase):

    @patch('recommender.Entrez.esearch')
    @patch('recommender.Entrez.efetch')
    def test_fetch_pubmed(self, mock_efetch, mock_esearch):
        # Mock the Entrez search
        mock_esearch.return_value.read.return_value = {
            "IdList": ["12345", "67890"]
        }

        # Mock the Entrez fetch
        mock_efetch.return_value.read.return_value = """\
        PMID- 12345
        TI  - Test Article 1
        AB  - Abstract for article 1
        AU  - Author1
        AU  - Author2
        JT  - Journal1
        DP  - 2024
        
        PMID- 67890
        TI  - Test Article 2
        AB  - Abstract for article 2
        AU  - Author3
        JT  - Journal2
        DP  - 2023
        """

        # Convert mocked fetch output to Medline records
        records = [
            {
                "PMID": "12345",
                "TI": "Test Article 1",
                "AB": "Abstract for article 1",
                "AU": ["Author1", "Author2"],
                "JT": "Journal1",
                "DP": "2024"
            },
            {
                "PMID": "67890",
                "TI": "Test Article 2",
                "AB": "Abstract for article 2",
                "AU": ["Author3"],
                "JT": "Journal2",
                "DP": "2023"
            }
        ]

        mock_efetch.return_value = MagicMock()
        mock_efetch.return_value.__iter__.return_value = records

        result_df = app.fetch_pubmed("test query", max_results=10)

        # Assertions
        self.assertEqual(len(result_df), 2)
        self.assertEqual(result_df["Title"].iloc[0], "Test Article 1")
        self.assertEqual(result_df["Abstract"].iloc[1], "Abstract for article 2")

    @patch('recommender.SentenceTransformer')
    def test_encode_abstracts(self, mock_model):
        # Mock model.encode
        mock_model.return_value.encode.return_value = np.array([[0.1, 0.2], [0.3, 0.4]])

        model = mock_model()
        abstracts = ["Abstract 1", "Abstract 2"]
        embeddings = app.encode_abstracts(abstracts, model)

        # Assertions
        self.assertIsNotNone(embeddings)
        self.assertEqual(embeddings.shape, (2, 2))
        np.testing.assert_array_almost_equal(embeddings, np.array([[0.1, 0.2], [0.3, 0.4]]))

    def test_build_faiss_index(self):
        embeddings = np.array([[0.1, 0.2], [0.3, 0.4]]).astype('float32')
        index = app.build_faiss_index(embeddings)

        # Assertions
        self.assertIsInstance(index, faiss.IndexFlatIP)
        self.assertEqual(index.ntotal, 2)  # 2 embeddings added

    def test_save_and_load_faiss_index(self):
        embeddings = np.array([[0.1, 0.2], [0.3, 0.4]]).astype('float32')
        index = app.build_faiss_index(embeddings)

        # Save the index and embeddings
        embedding_path = "test_embeddings.pkl"
        index_path = "test_faiss.index"
        app.save_faiss_index(embeddings, index, embedding_path, index_path)

        # Load the index and embeddings
        loaded_index, loaded_embeddings = app.load_faiss_index(embedding_path, index_path)

        # Assertions
        self.assertIsNotNone(loaded_index)
        self.assertTrue(os.path.exists(embedding_path))
        self.assertTrue(os.path.exists(index_path))
        np.testing.assert_array_almost_equal(embeddings, loaded_embeddings)

        # Cleanup
        os.remove(embedding_path)
        os.remove(index_path)

    def test_recommend_papers(self):
        # Mock data
        df = pd.DataFrame({
            "Title": ["Paper 1", "Paper 2", "Paper 3"],
            "Abstract": ["Abstract 1", "Abstract 2", "Abstract 3"]
        })
        embeddings = np.array([[0.1, 0.2], [0.3, 0.4], [0.5, 0.6]]).astype('float32')
        index = app.build_faiss_index(embeddings)

        # Query embedding
        query_embedding = np.array([[0.15, 0.25]]).astype('float32')

        # Recommendations
        recommendations = app.recommend_papers(query_embedding[0], index, df, top_k=2)

        # Assertions
        self.assertEqual(len(recommendations), 2)
        self.assertIn("Paper 1", recommendations["Title"].values)
        self.assertIn("Paper 2", recommendations["Title"].values)

if __name__ == "__main__":
    unittest.main()
