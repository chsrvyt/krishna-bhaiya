from pydantic import ValidationError
import pytest
from agent.qa import deterministic_issues, swap_test
from agent.schemas import Contact, Email
from agent.stages.stage0_icp import _rubric_from_doc

BASE = dict(contact="Ana López", company="Minería Real", language="Spanish", subject="Pond inspections at Minería Real", body="Ana, Minería Real announced a pond expansion. Anglo American uses FlytBase. Would a 15-minute conversation help?", english_translation="Ana, Minería Real announced a pond expansion. Anglo American uses FlytBase. Would a 15-minute conversation help?", evidence=[{"claim_in_email":"pond expansion", "source_url":"https://example.com/news", "source_date":"2026-01-01"}], persona="Ops", hook_type="expansion")

def test_schema_validation_rejects_non_url():
    bad = BASE | {"evidence": [{"claim_in_email":"x", "source_url":"not a url", "source_date":"today"}]}
    with pytest.raises(ValidationError): Email.model_validate(bad)

def test_banned_phrase_and_placeholder_detection():
    email = Email.model_validate(BASE | {"body": "I hope this email finds you well, {first_name}. Anglo American uses FlytBase."})
    assert "banned phrase detected" in deterministic_issues(email)
    assert "placeholder detected" in deterministic_issues(email)

def test_swap_test_flags_generic_copy():
    email = Email.model_validate(BASE | {"body": "Your recent expansion matters. Anglo American uses FlytBase. Would a 15-minute conversation help?"})
    assert swap_test(email)

def test_not_found_contact_is_allowed_without_email():
    contact = Contact(company="Minería Real", full_name="NOT_FOUND", title="Director of Operations", seniority="unknown", role_match="Ops", email_status="not_found", source_url="https://example.com/company", source_date="2026-01-01", confidence="low")
    assert contact.full_name == "NOT_FOUND"

def test_not_found_cannot_include_email():
    with pytest.raises(ValidationError):
        Contact(company="Minería Real", full_name="NOT_FOUND", title="Director", seniority="unknown", role_match="Ops", email="person@example.com", email_status="not_found", source_url="https://example.com/company", source_date="2026-01-01", confidence="low")


def test_icp_rubric_is_parsed_from_the_canonical_document():
    document = "| Criterion | Weight | Signal |\n| A | 20 | one |\n| B | 20 | two |\n| C | 15 | three |\n| D | 10 | four |\n| E | 10 | five |\n| F | 15 | six |\n| G | 10 | seven |"
    assert [item.weight for item in _rubric_from_doc(document)] == [20, 20, 15, 10, 10, 15, 10]
