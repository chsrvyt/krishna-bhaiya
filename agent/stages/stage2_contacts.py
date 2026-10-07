from __future__ import annotations
from pydantic import RootModel
from ..llm import LLM
from ..schemas import Account, Contact
from .common import prompt, context

class Contacts(RootModel[list[Contact]]): pass

async def run_one(llm: LLM, account: Account, contacts_per_account: int) -> list[Contact]:
    result = await llm.structured("stage2_contacts", prompt("02_contact_discovery.md") + context(account=account.model_dump(), contacts_per_account=contacts_per_account), Contacts, web_search=True)
    contacts = result.root[:contacts_per_account]
    if not contacts:
        evidence = account.fit_reasoning[0]
        return [Contact(company=account.company, full_name="NOT_FOUND", title="Head/VP/Director of Operations", seniority="unknown", role_match="Ops", email_status="not_found", source_url=evidence.source_url, source_date=evidence.source_date, confidence="low")]
    return contacts
