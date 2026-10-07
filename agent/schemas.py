"""Strict, source-aware contracts for pipeline artifacts."""
from __future__ import annotations

from datetime import date
from typing import Literal
from pydantic import BaseModel, Field, field_validator, model_validator


class Source(BaseModel):
    claim: str = Field(min_length=3)
    url: str
    date: str

    @field_validator("url")
    @classmethod
    def public_url(cls, value: str) -> str:
        if not value.startswith(("https://", "http://")):
            raise ValueError("source URL must be an http(s) URL")
        return value


class RubricItem(BaseModel):
    criterion: str
    weight: int = Field(ge=0, le=100)
    evidence_to_look_for: str


class ICPProfile(BaseModel):
    reference_account: str
    profile: dict[str, str]
    rubric: list[RubricItem]
    sources: list[Source]



class FitReason(BaseModel):
    point: str
    source_url: str
    source_date: str


class Account(BaseModel):
    company: str
    parent: str | None = None
    country: str
    sites: list[str] = Field(min_length=1)
    commodity: str
    icp_score: int = Field(ge=0, le=100)
    score_breakdown: dict[str, int]
    fit_reasoning: list[FitReason] = Field(min_length=3)
    sqm_similarity: str
    risk_flags: list[str] = []
    tier: Literal["A", "B", "exclude"]

    @field_validator("fit_reasoning")
    @classmethod
    def sourced_reasons(cls, value: list[FitReason]) -> list[FitReason]:
        if len({item.source_url for item in value}) < 2:
            raise ValueError("at least two distinct sources are required")
        return value


class Contact(BaseModel):
    company: str
    full_name: str
    title: str
    seniority: str
    role_match: Literal["Ops", "HSE", "Site"]
    linkedin_url: str | None = None
    email: str | None = None
    email_status: Literal["verified", "pattern_guess", "not_found"]
    source_url: str
    source_date: str
    confidence: Literal["high", "med", "low"]

    @field_validator("full_name")
    @classmethod
    def not_found_has_target(cls, value: str) -> str:
        if value == "NOT_FOUND":
            return value
        if len(value.split()) < 2:
            raise ValueError("contact must have a real full name or NOT_FOUND")
        return value

    @model_validator(mode="after")
    def email_consistency(self):
        if self.email_status == "not_found" and self.email:
            raise ValueError("not_found email status cannot contain an email")
        return self


class Evidence(BaseModel):
    claim_in_email: str
    source_url: str
    source_date: str

    @field_validator("source_url")
    @classmethod
    def public_url(cls, value: str) -> str:
        if not value.startswith(("https://", "http://")):
            raise ValueError("evidence URL must be an http(s) URL")
        return value


class Email(BaseModel):
    contact: str
    company: str
    language: str
    subject: str
    body: str
    english_translation: str
    evidence: list[Evidence] = Field(min_length=1)
    persona: Literal["Ops", "HSE", "Site"]
    hook_type: Literal["news", "expansion", "ops_footprint", "tech_signal"]


class QAResult(BaseModel):
    passed: bool = Field(alias="pass")
    issues: list[str]
    unsupported_claims: list[str]
    personalization_score: int = Field(ge=1, le=5)
    tone_score: int = Field(ge=1, le=5)
    reply_likelihood: int = Field(ge=1, le=5)
    suggested_fix: str = ""

    model_config = {"populate_by_name": True}
