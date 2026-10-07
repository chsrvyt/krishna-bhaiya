from __future__ import annotations
from ..llm import LLM
from ..schemas import Email, QAResult
from .common import prompt, context

async def run_one(llm: LLM, email: Email, research: str) -> QAResult:
    return await llm.structured("stage5_qa", prompt("05_email_qa.md") + context(email=email.model_dump(), research_brief=research), QAResult, web_search=False)
