"""Deterministic guardrails complement the separate LLM QA call."""
from __future__ import annotations
import re
from .schemas import Email

BANNED = ("i hope this email finds you well", "revolutionary", "game-changing", "synergy", "touch base")
ALLOWED_PROOF = {"Shell", "Anglo American", "CSX", "Airbus", "Statnett", "Dole", "UK Police"}


def deterministic_issues(email: Email) -> list[str]:
    issues: list[str] = []
    combined = f"{email.subject} {email.body}".lower()
    if len(email.subject.split()) > 7:
        issues.append("subject exceeds 7 words")
    if len(email.body.split()) > 110:
        issues.append("body exceeds 110 words")
    if any(term in combined for term in BANNED):
        issues.append("banned phrase detected")
    if re.search(r"\{[^}]+\}|\[[^\]]+\]", email.subject + email.body):
        issues.append("placeholder detected")
    if not any(proof.lower() in combined for proof in ALLOWED_PROOF):
        issues.append("missing allowed FlytBase proof point")
    if not email.evidence:
        issues.append("email has no evidence")
    return issues


def swap_test(email: Email) -> bool:
    """True means too generic: the actual body omits both named company and contact."""
    text = email.body.lower()
    return email.company.lower() not in text and email.contact.split()[0].lower() not in text
