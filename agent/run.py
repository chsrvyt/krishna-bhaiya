"""Run the FlytBase BDR pipeline against live provider/search tools."""
from __future__ import annotations
import argparse, asyncio, csv, json, re
from datetime import datetime
from pathlib import Path
import sys
import yaml
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from agent.llm import LLM
from agent.qa import deterministic_issues, swap_test
from agent.tools import RunLogger
from agent.stages import stage0_icp, stage1_accounts, stage2_contacts, stage3_research, stage4_email, stage5_qa


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def write_csv(path: Path, rows: list[dict]) -> None:
    fields = sorted({key for row in rows for key in row})
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader(); writer.writerows(rows)


def safe_name(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")


async def pipeline(args: argparse.Namespace) -> Path:
    load_dotenv(ROOT / ".env")
    brief = yaml.safe_load(Path(args.brief).read_text(encoding="utf-8"))
    stamp = datetime.now().strftime("%Y%m%dT%H%M%S")
    run_dir = ROOT / "runs" / stamp
    (run_dir / "research").mkdir(parents=True)
    (run_dir / "emails").mkdir()
    logger = RunLogger(run_dir)
    (run_dir / "failures.log").touch()
    print(f"Run folder: {run_dir}")
    try:
        llm = LLM(logger)
    except Exception as exc:
        await logger.failure("startup", {"provider": "environment"}, str(exc), "Add valid credentials to .env (copy .env.example).")
        print(f"Startup failed visibly: {exc}")
        return run_dir

    print("Stage 0/5: ICP model")
    try:
        icp = await stage0_icp.run(llm, brief)
        write_json(run_dir / "icp_profile.json", icp.model_dump())
    except Exception as exc:
        await logger.failure("stage0_icp", brief, str(exc), "Check search/provider access and try again.")
        return run_dir
    if args.only_stage == 0: return run_dir

    print("Stage 1/5: account identification")
    try:
        accounts = await stage1_accounts.run(llm, brief, icp, args.max_accounts)
        rows = [a.model_dump() for a in accounts]
        write_json(run_dir / "accounts.json", rows)
        write_csv(run_dir / "accounts.csv", [{**{k: v for k,v in r.items() if not isinstance(v, (dict,list))}, "sites": "; ".join(r["sites"]), "fit_reasoning": json.dumps(r["fit_reasoning"], ensure_ascii=False), "risk_flags": "; ".join(r["risk_flags"])} for r in rows])
    except Exception as exc:
        await logger.failure("stage1_accounts", brief, str(exc), "Check provider result and source quality.")
        return run_dir
    if args.only_stage == 1: return run_dir

    print("Stage 2/5: contact discovery")
    sem = asyncio.Semaphore(args.concurrency)
    async def contacts_for(account):
        async with sem:
            try: return await stage2_contacts.run_one(llm, account, args.contacts_per_account)
            except Exception as exc:
                await logger.failure("stage2_contacts", account.company, str(exc), "Retry with a narrower title/site query.")
                return []
    nested = await asyncio.gather(*(contacts_for(a) for a in accounts))
    contacts = [c for group in nested for c in group]
    write_csv(run_dir / "contacts.csv", [c.model_dump() for c in contacts])
    if args.only_stage == 2: return run_dir

    print("Stage 3/5: account research")
    research: dict[str, str] = {}
    async def research_for(account):
        async with sem:
            try:
                text = await stage3_research.run_one(llm, account, [c for c in contacts if c.company == account.company])
                research[account.company] = text
                (run_dir / "research" / f"{safe_name(account.company)}.md").write_text(text, encoding="utf-8")
            except Exception as exc:
                await logger.failure("stage3_research", account.company, str(exc), "Broaden sources or retry after rate limit.")
    await asyncio.gather(*(research_for(a) for a in accounts))
    if args.only_stage == 3: return run_dir

    print("Stages 4-5/5: email generation and independent QA")
    emails, reports = [], []
    for contact in contacts:
        if contact.full_name == "NOT_FOUND":
            await logger.failure("stage4_email", contact.company, "No named contact", "Find a public current operations/HSE/site leader before drafting.")
            continue
        try:
            feedback = ""
            for attempt in range(3):
                email = await stage4_email.run_one(llm, brief, contact, research.get(contact.company, ""), feedback)
                issues = deterministic_issues(email)
                if swap_test(email): issues.append("swap test failed: generic email")
                qa = await stage5_qa.run_one(llm, email, research.get(contact.company, ""))
                report = qa.model_dump(by_alias=True) | {"contact": contact.full_name, "deterministic_issues": issues, "attempt": attempt + 1}
                if qa.passed and not issues:
                    emails.append(email); reports.append(report)
                    (run_dir / "emails" / f"{safe_name(contact.full_name)}.md").write_text(f"# {email.subject}\n\n{email.body}\n\nEnglish: {email.english_translation}\n", encoding="utf-8")
                    break
                feedback = json.dumps(report, ensure_ascii=False)
                if attempt == 2:
                    reports.append(report)
                    await logger.failure("stage5_qa", contact.full_name, feedback, "Review source-to-claim mapping and rewrite with a specific FACT hook.")
        except Exception as exc:
            await logger.failure("stage4_5", contact.full_name, str(exc), "Check the research brief and provider availability.")
    write_json(run_dir / "emails.json", [e.model_dump() for e in emails])
    write_json(run_dir / "qa_report.json", reports)
    print(f"Complete: {len(emails)} QA-passed email(s).")
    return run_dir


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--brief", default="brief.yaml")
    parser.add_argument("--max-accounts", type=int, default=8)
    parser.add_argument("--contacts-per-account", type=int, default=2)
    parser.add_argument("--concurrency", type=int, default=3)
    parser.add_argument("--only-stage", type=int, choices=range(6))
    args = parser.parse_args()
    asyncio.run(pipeline(args))

if __name__ == "__main__": main()
