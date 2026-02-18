import pytest
from app.domain import ner

def test_extract_entities_empty():
    assert ner.extract_entities("") == []

def test_extract_entities_mock(mocker):
    # Mock spaCy behavior
    mock_nlp = mocker.Mock()
    mock_doc = mocker.Mock()

    mock_ent = mocker.Mock()
    mock_ent.text = "Fabio"
    mock_ent.label_ = "PERSON"
    mock_ent.start_char = 0
    mock_ent.end_char = 5

    mock_doc.ents = [mock_ent]
    mock_nlp.return_value = mock_doc

    # Patch the models
    mocker.patch.object(ner, "nlp_pt", mock_nlp)
    mocker.patch.object(ner, "nlp_en", mock_nlp)

    # Test extraction
    entities = ner.extract_entities("Fabio", lang_hint="por")

    assert len(entities) == 1
    assert entities[0]["text"] == "Fabio"
    assert entities[0]["label"] == "PER"
    assert entities[0]["start"] == 0
    assert entities[0]["end"] == 5

def test_model_selection(mocker):
    mock_nlp_pt = mocker.Mock()
    mock_nlp_en = mocker.Mock()

    mock_doc_pt = mocker.Mock()
    mock_doc_pt.ents = []
    mock_nlp_pt.return_value = mock_doc_pt

    mock_doc_en = mocker.Mock()
    mock_doc_en.ents = []
    mock_nlp_en.return_value = mock_doc_en

    # Patch models
    mocker.patch.object(ner, "nlp_pt", mock_nlp_pt)
    mocker.patch.object(ner, "nlp_en", mock_nlp_en)

    # "por" uses nlp_pt
    ner.extract_entities("test", lang_hint="por")
    mock_nlp_pt.assert_called_once()
    mock_nlp_en.assert_not_called()

    mock_nlp_pt.reset_mock()
    mock_nlp_en.reset_mock()

    # "eng" uses nlp_en
    ner.extract_entities("test", lang_hint="eng")
    mock_nlp_en.assert_called_once()
    mock_nlp_pt.assert_not_called()

    mock_nlp_pt.reset_mock()
    mock_nlp_en.reset_mock()

    # "eng+por" should prioritize nlp_pt based on current logic
    ner.extract_entities("test", lang_hint="eng+por")
    mock_nlp_pt.assert_called_once()
    mock_nlp_en.assert_not_called()

def test_model_missing(mocker):
    # Simulate missing models
    mocker.patch.object(ner, "nlp_pt", None)
    mocker.patch.object(ner, "nlp_en", None)

    assert ner.extract_entities("test", lang_hint="por") == []

    # Simulate missing PT, fallback to EN
    mock_nlp_en = mocker.Mock()
    mock_doc = mocker.Mock()
    mock_doc.ents = []
    mock_nlp_en.return_value = mock_doc

    mocker.patch.object(ner, "nlp_pt", None)
    mocker.patch.object(ner, "nlp_en", mock_nlp_en)

    ner.extract_entities("test", lang_hint="por")
    mock_nlp_en.assert_called_once()
