# ner_processor.py
import spacy
from scispacy.linking import EntityLinker
from constants import UMLS_TUI_TO_CATEGORY

def setup_ner_model():
    """Initialize the NER model with UMLS linking"""
    nlp = spacy.load("en_core_sci_md")
    nlp.add_pipe("scispacy_linker", config={"resolve_abbreviations": True, "linker_name": "umls"})
    return nlp

def get_umls_category(cui, linker):
    """Get UMLS category for a given CUI"""
    tuis = linker.kb.cui_to_entity[cui].types
    for tui in tuis:
        category = UMLS_TUI_TO_CATEGORY.get(tui)
        if category:
            return category
    return "OTHER"

def extract_medical_terms(text, nlp):
    """Extract medical terms using NER model"""
    doc = nlp(text)
    linker = nlp.get_pipe("scispacy_linker")
    
    entities = []
    for ent in doc.ents:
        if ent._.kb_ents:
            cui, score = ent._.kb_ents[0]
            category = get_umls_category(cui, linker)
            entities.append({
                'Term': ent.text,
                'Category': category,
                'UMLS Concept ID': cui,
                'Similarity Score': score
            })
    return entities