from __future__ import annotations
from pydantic import RootModel
from ..llm import LLM
from ..schemas import Account, ICPProfile
from .common import prompt, context

class Accounts(RootModel[list[Account]]): pass

async def run(llm: LLM, brief: dict, icp: ICPProfile, max_accounts: int) -> list[Account]:
    result = await llm.structured("stage1_accounts", prompt("01_account_identification.md") + context(brief=brief, icp_profile=icp.model_dump(), max_accounts=max_accounts), Accounts, web_search=True)
    return sorted([a for a in result.root if a.icp_score >= 60 and a.company.lower() not in brief["reference_account"].lower()], key=lambda a: a.icp_score, reverse=True)[:max_accounts]
