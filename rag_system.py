# rag_system.py
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Union

class RAGSystem:
    def __init__(self, reference_file_path: str):
        """Initialize RAG system with reference data"""
        # Load reference data
        self.df = pd.read_csv(reference_file_path)
        
        # Initialize model directly from HuggingFace
        self.model = SentenceTransformer('pritamdeka/BioBERT-mnli-snli-scinli-scitail-mednli-stsb')
        
        # Pre-compute reference embeddings
        reference_texts = self.df.apply(
            lambda row: f"{row['CODE']} {row['Medical term']} {row['Description']}", 
            axis=1
        ).tolist()
        self.reference_embeddings = self.model.encode(
            reference_texts, 
            convert_to_tensor=True, 
            show_progress_bar=True
        )

    def semantic_search(self, keywords: Union[str, List[str]], top_k: int = 3) -> Dict:
        """Perform semantic search using cosine similarity"""
        if isinstance(keywords, str):
            keywords = [keywords]
            
        # Encode keywords
        keyword_embeddings = self.model.encode(keywords, convert_to_tensor=True)
        
        # Calculate similarities
        similarities = np.inner(keyword_embeddings, self.reference_embeddings)
        
        results = {}
        for i, keyword in enumerate(keywords):
            # Get top k indices
            top_indices = np.argsort(similarities[i])[-top_k:][::-1]
            
            search_results = []
            for idx in top_indices:
                result_row = self.df.iloc[idx]
                search_results.append({
                    "CODE": result_row['CODE'],
                    "Medical term": result_row['Medical term'],
                    "Description": result_row['Description'],
                    "Similarity": float(similarities[i][idx])
                })
            results[keyword] = search_results
            
        return results

    def exact_match(self, keywords: Union[str, List[str]], top_k: int = 3) -> Dict:
        """Perform exact match search"""
        if isinstance(keywords, str):
            keywords = [keywords]
            
        columns = ['CODE', 'Medical term', 'Description']
        results = {}
        
        for keyword in keywords:
            search_results = []
            for column in columns:
                matches = self.df[self.df[column].str.contains(keyword, case=False, na=False)]
                for _, row in matches.iterrows():
                    search_results.append({
                        "CODE": row['CODE'],
                        "Medical term": row['Medical term'],
                        "Description": row['Description'],
                        "Matched Column": column
                    })
            
            # Sort and limit results
            search_results.sort(key=lambda x: len(x[x['Matched Column']]))
            results[keyword] = search_results[:top_k]
            
        return results

# constants.py
UMLS_TUI_TO_CATEGORY = {
    # [Keep your existing UMLS_TUI_TO_CATEGORY dictionary here]
    # I'm not including it to save space, but it should be the same as in your original code
}