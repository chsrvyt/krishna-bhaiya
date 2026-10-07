from __future__ import annotations
from ..llm import LLM
from ..schemas import ICPProfile, RubricItem
from .common import ROOT, prompt, context

async def run(llm: LLM, brief: dict) -> ICPProfile:
    rubric = (ROOT / "docs" / "ICP.md").read_text(encoding="utf-8")
    result = await llm.structured("stage0_icp", prompt("00_icp_model.md") + context(brief=brief, icp_model=rubric), ICPProfile, web_search=True)
    # The rubric is assignment configuration, not a web-derived claim. Read it
    # from its canonical runtime file so label variants cannot trigger extra LLM
    # calls or alter scoring weights.
    result.rubric = _rubric_from_doc(rubric)
    result.profile = {key: ("unverified" if "no specific information" in value.lower() else value)
                      for key, value in result.profile.items()}
    return result


def _rubric_from_doc(document: str) -> list[RubricItem]:
    items: list[RubricItem] = []
    for line in document.splitlines():
        columns = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(columns) == 3 and columns[1].isdigit():
            items.append(RubricItem(criterion=columns[0], weight=int(columns[1]), evidence_to_look_for=columns[2]))
    if len(items) != 7:
        raise RuntimeError("Could not parse the seven ICP rubric rows from docs/ICP.md")
    return items
