# app.py
import streamlit as st
from ner_processor import setup_ner_model, extract_medical_terms
from rag_system import RAGSystem
import pandas as pd
from typing import Dict, List
import time

def initialize_session_state():
    """Initialize or reset session state variables"""
    if 'processing' not in st.session_state:
        st.session_state.processing = False
    
    # Initialize models if they don't exist
    if 'ner_model' not in st.session_state:
        with st.spinner('Loading NER model...'):
            try:
                st.session_state.ner_model = setup_ner_model()
                st.sidebar.success("✓ NER Model loaded")
            except Exception as e:
                st.error(f"Error loading NER model: {str(e)}")
                st.session_state.ner_model = None
                return False
    
    if 'rag_system' not in st.session_state:
        with st.spinner('Loading RAG system...'):
            try:
                st.session_state.rag_system = RAGSystem('Section111ValidICD10-Jan2024.csv')
                st.sidebar.success("✓ RAG System loaded")
            except Exception as e:
                st.error(f"Error loading RAG system: {str(e)}")
                st.session_state.rag_system = None
                return False
    
    return True

def process_medical_text(input_text: str) -> Dict:
    """Process medical text and return results"""
    results = {
        'success': False,
        'ner_results': None,
        'semantic_results': None,
        'exact_results': None,
        'error': None
    }
    
    try:
        # Extract medical terms
        ner_results = extract_medical_terms(input_text, st.session_state.ner_model)
        results['ner_results'] = ner_results
        
        if ner_results:
            # Get keywords for RAG processing
            keywords = [entity['Term'] for entity in ner_results]
            
            # Get RAG results
            semantic_results = st.session_state.rag_system.semantic_search(keywords)
            exact_results = st.session_state.rag_system.exact_match(keywords)
            
            results['semantic_results'] = semantic_results
            results['exact_results'] = exact_results
            results['success'] = True
        else:
            results['success'] = True  # Still successful, just no terms found
            
    except Exception as e:
        results['error'] = str(e)
        
    return results

def display_results(input_text: str, results: Dict):
    """Display processing results in the Streamlit UI"""
    # Display input text
    st.subheader("Input Text:")
    st.write(input_text)
    
    # Display NER results
    st.subheader("Identified Medical Terms:")
    if results['ner_results']:
        ner_df = pd.DataFrame(results['ner_results'])
        st.dataframe(ner_df)
    else:
        st.info("No medical terms were identified in the input text.")
        return
    
    # Display RAG results
    if results['semantic_results'] and results['exact_results']:
        st.subheader("Medical Codes Results:")
        
        for keyword in results['semantic_results'].keys():
            st.markdown(f"### Term: {keyword}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Semantic Matches:**")
                if results['semantic_results'][keyword]:
                    df = pd.DataFrame(results['semantic_results'][keyword])
                    st.dataframe(df)
                else:
                    st.info("No semantic matches found")
            
            with col2:
                st.markdown("**Exact Matches:**")
                if results['exact_results'][keyword]:
                    df = pd.DataFrame(results['exact_results'][keyword])
                    st.dataframe(df)
                else:
                    st.info("No exact matches found")

def main():
    st.set_page_config(page_title="Medical Coding Assistant", layout="wide")
    st.title("Medical Coding Assistant")
    
    # Initialize session state and models
    if not initialize_session_state():
        st.error("Failed to initialize the application. Please refresh the page.")
        return
    
    # Reset processing state when new text is entered
    if 'last_input' not in st.session_state:
        st.session_state.last_input = ''
    
    # Text input
    input_text = st.text_area(
        "Enter medical text (e.g., 'Patient presents with acute bronchitis and fever'):",
        height=200,
        key='input_text'
    )
    
    # Process button
    if st.button("Process Text", key='process_button', disabled=st.session_state.processing):
        if not input_text:
            st.warning("Please enter some medical text to process.")
            return
        
        try:
            # Set processing state
            st.session_state.processing = True
            st.session_state.last_input = input_text
            
            # Show processing status
            status = st.empty()
            status.text("Processing text...")
            
            # Process the text
            results = process_medical_text(input_text)
            
            if results['success']:
                display_results(input_text, results)
            else:
                st.error(f"Processing failed: {results['error']}")
                
            # Clear status and reset processing state
            status.empty()
            
        except Exception as e:
            st.error(f"An unexpected error occurred: {str(e)}")
            st.error("Please try again or contact support if the problem persists.")
            
        finally:
            # Ensure processing state is reset
            st.session_state.processing = False
            
    # Add system status information
    st.sidebar.write("System Status:")
    st.sidebar.write(f"Processing: {'Yes' if st.session_state.processing else 'No'}")
    st.sidebar.write(f"Models Loaded: {'Yes' if st.session_state.ner_model and st.session_state.rag_system else 'No'}")

if __name__ == '__main__':
    main()