import litellm
import instructor
from litellm import completion
from app.model.StructuredSchema import StructuredDocumentData, DocumentEntity
from app.domain import ner
import logging

log = logging.getLogger("uvicorn")

def extract_structured_data(
    text: str,
    provider: str = "local_tesseract",
    model_name: str = "",
    lang_hint: str = "eng+por"
) -> StructuredDocumentData:
    """
    Extracts structured data from raw text.
    If provider is 'local_tesseract', returns a fallback structure using heuristics and spaCy.
    Otherwise, uses litellm + instructor to ask the specified model for the StructuredDocumentData.
    """

    if provider == "local_tesseract" or not model_name:
        # Fallback to local heuristic extraction
        log.info("Using local fallback for structured extraction (no LLM)")

        # Extract entities using existing spaCy NER
        spacy_entities = ner.extract_entities(text, lang_hint=lang_hint)
        entities = [
            DocumentEntity(text=e["text"], label=e["label"])
            for e in spacy_entities
        ]

        return StructuredDocumentData(
            document_type="unknown",
            key_values=[],
            tables=[],
            entities=entities,
            text_summary=f"Fallback extraction. Extracted {len(text)} characters of text."
        )

    # Use litellm with instructor to get structured JSON
    log.info(f"Using LLM for structured extraction: provider={provider}, model={model_name}")

    # Patch litellm completion with instructor
    client = instructor.from_litellm(completion)

    # Prefix the model with the provider if litellm requires it
    # litellm format is usually "provider/model_name"
    full_model_name = f"{provider}/{model_name}" if "/" not in model_name and provider != "openai" else model_name

    prompt = (
        "You are an expert data extraction assistant. I will provide you with the raw OCR text of a document. "
        "Your task is to analyze the text and extract structured information, including the type of the document, "
        "any key-value pairs (like invoice numbers, dates, totals, names), any tables you can identify, "
        "and a brief summary. Also extract important named entities.\n\n"
        "Here is the raw document text:\n"
        "------------------\n"
        f"{text}\n"
        "------------------\n"
    )

    try:
        # instructor will handle forcing the StructuredDocumentData schema
        structured_data = client.chat.completions.create(
            model=full_model_name,
            messages=[
                {"role": "system", "content": "You are a precise data extraction AI."},
                {"role": "user", "content": prompt}
            ],
            response_model=StructuredDocumentData,
            max_tokens=4096,
        )
        return structured_data
    except Exception as e:
        log.error(f"Error during LLM structured extraction: {e}")
        # Return fallback on error
        return extract_structured_data(text, "local_tesseract", "", lang_hint)
