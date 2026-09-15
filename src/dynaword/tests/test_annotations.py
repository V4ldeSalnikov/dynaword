from pathlib import Path

from dynaword.annotations.propella import (
    TRUNCATION_TAG,
    AnnotationResponse,
    create_messages,
)


VALID_RESPONSE = """{"content_integrity":"complete","content_ratio":"complete_content","content_length":"minimal","one_sentence_description":"A short question and answer.","content_type":["qa_structured"],"business_sector":["general_interest"],"technical_content":["non_technical"],"information_density":"dense","content_quality":"good","audience_level":"general","commercial_bias":"none","time_sensitivity":"evergreen","content_safety":"safe","educational_value":"none","reasoning_indicators":"none","pii_presence":"no_pii","regional_relevance":["culturally_neutral"],"country_relevance":["none"]}"""


def test_annotation_response_parses_official_schema():
    parsed = AnnotationResponse.model_validate_json(VALID_RESPONSE)

    assert parsed.time_sensitivity == "evergreen"
    assert parsed.country_relevance == ["none"]


def test_inference_example_matches_official_model_card_shape():
    inference_path = Path(__file__).parents[1] / "annotations" / "inference.py"
    source = inference_path.read_text(encoding="utf-8")

    assert "from openai import OpenAI" in source
    assert "from propella import (" in source
    assert 'document = "Hi, its me Max."' in source
    assert 'client = OpenAI(base_url="http://localhost:8000/v1", api_key="EMPTY")' in source
    assert "response = client.chat.completions.create(" in source
    assert 'model="ellamind/propella-1-4b",' in source
    assert '"schema": get_annotation_response_schema(flatten=True, compact_whitespace=True),' in source
    assert "result = AnnotationResponse.model_validate_json(response_content)" in source
    assert "print(result.model_dump_json(indent=4))" in source


def test_create_messages_truncates_content():
    messages = create_messages("abcdef", max_content_chars=3)

    assert messages[1]["content"].startswith("<start_of_document>\nabc")
    assert TRUNCATION_TAG in messages[1]["content"]
