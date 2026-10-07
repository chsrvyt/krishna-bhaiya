from __future__ import annotations
from ..llm import LLM
from ..schemas import Contact, Email
from .common import prompt, context

async def run_one(llm: LLM, brief: dict, contact: Contact, research: str, qa_feedback: str = "") -> Email:
    instruction = prompt("04_email_generation.md") + context(brief=brief, contact=contact.model_dump(), research_brief=research, qa_feedback=qa_feedback)
    return await llm.structured("stage4_email", instruction, Email, web_search=False)
