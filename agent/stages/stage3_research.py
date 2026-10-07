from __future__ import annotations
from ..llm import LLM
from ..schemas import Account, Contact
from .common import prompt, context

async def run_one(llm: LLM, account: Account, contacts: list[Contact]) -> str:
    # Markdown is deliberately retained verbatim, then deterministic source checks run in QA.
    return await llm_text(llm, "stage3_research", prompt("03_account_research.md") + context(account=account.model_dump(), contacts=[c.model_dump() for c in contacts]))

async def llm_text(llm: LLM, stage: str, text: str) -> str:
    from pydantic import BaseModel
    class Markdown(BaseModel): content: str
    result = await llm.structured(stage, text + "\nReturn a JSON object containing one `content` field with the required Markdown.", Markdown, web_search=True)
    return result.content
