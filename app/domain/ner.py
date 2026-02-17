import spacy
from typing import List, Dict, Any, Optional
import logging

log = logging.getLogger("uvicorn")

# Load models globally
# handling potentially missing models gracefully
nlp_en: Optional[spacy.language.Language] = None
nlp_pt: Optional[spacy.language.Language] = None

try:
    nlp_en = spacy.load("en_core_web_sm")
    log.info("Loaded spaCy model: en_core_web_sm")
except OSError:
    log.warning("spaCy model 'en_core_web_sm' not found. NER for English might not work.")

try:
    nlp_pt = spacy.load("pt_core_news_sm")
    log.info("Loaded spaCy model: pt_core_news_sm")
except OSError:
    log.warning("spaCy model 'pt_core_news_sm' not found. NER for Portuguese might not work.")

def extract_entities(text: str, lang_hint: str = "eng+por") -> List[Dict[str, Any]]:
    """
    Extracts entities (PER, LOC, ORG) from text using spaCy.

    Args:
        text (str): The input text.
        lang_hint (str): Language hint from the request (e.g., 'por', 'eng', 'eng+por', 'auto').

    Returns:
        List[Dict[str, Any]]: A list of entities with 'text', 'label', 'start', 'end'.
    """
    if not text:
        return []

    nlp = _select_model(lang_hint)

    if not nlp:
        log.warning("No suitable spaCy model found for NER extraction.")
        return []

    doc = nlp(text)

    entities = []
    for ent in doc.ents:
        label = ent.label_

        # Normalize labels
        # spaCy English: PERSON, ORG, GPE, LOC
        # spaCy Portuguese: PER, ORG, LOC, MISC

        normalized_label = None

        if label in ["PER", "PERSON"]:
            normalized_label = "PER"
        elif label in ["ORG"]:
            normalized_label = "ORG"
        elif label in ["LOC", "GPE"]:
            normalized_label = "LOC"

        if normalized_label:
            entities.append({
                "text": ent.text,
                "label": normalized_label,
                "start": ent.start_char,
                "end": ent.end_char
            })

    return entities

def _select_model(lang_hint: str) -> Optional[spacy.language.Language]:
    """
    Selects the appropriate spaCy model based on the language hint.
    """
    # Normalize hint
    hint = lang_hint.lower()

    # Priority logic
    # If explicitly Portuguese or containing it (like 'eng+por'), prefer PT model
    # as it often handles English entities (names, orgs) reasonably well too,
    # while EN model on PT text fails badly.
    if "por" in hint:
        if nlp_pt:
            return nlp_pt
        if nlp_en:
            return nlp_en

    if "eng" in hint:
        if nlp_en:
            return nlp_en
        if nlp_pt:
            return nlp_pt

    # Default fallback
    if nlp_pt:
        return nlp_pt
    if nlp_en:
        return nlp_en

    return None
