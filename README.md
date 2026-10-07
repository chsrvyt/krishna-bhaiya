# FlytBase BDR Agent: LatAm Mining Outbound

An agentic pipeline that takes a campaign brief (`brief.yaml`) and produces: **accounts → contacts → research briefs → personalized emails**. The logic lives in `prompts/` and `agent/`; outputs land in `runs/<timestamp>/`.

> **Rule of this repo:** every email in `runs/` is machine-generated from the pipeline. Nothing is hand-written. Every factual claim in an email must trace to a source URL in the research brief.

## Input (`brief.yaml`)
```yaml
target_vertical: "Large-scale lithium, copper, iron ore mining in Latin America"
reference_account: "Sociedad Química y Minera de Chile (SQM)"
goal: "Book discovery calls with Head of Operations, VP HSE, Site Directors"
angle: "Autonomous drone inspection replacing contracted crews at hazardous 24/7 extraction sites"
flytbase_proof: ["Shell", "Anglo American", "CSX", "Airbus", "Statnett", "Dole", "UK Police"]
```

## Pipeline

| Stage | Prompt | Tools | Output |
|---|---|---|---|
| 0. ICP model | `prompts/00_icp_model.md` | LLM + web search | `icp_profile.json` |
| 1. Accounts | `prompts/01_account_identification.md` | LLM + web search | `accounts.json` / `.csv` |
| 2. Contacts | `prompts/02_contact_discovery.md` | web search, Apollo/Hunter (optional) | `contacts.csv` |
| 3. Research | `prompts/03_account_research.md` | web search + page fetch | `research/<account>.md` |
| 4. Emails | `prompts/04_email_generation.md` | LLM | `emails/<contact>.md` |
| 5. QA gate | `prompts/05_email_qa.md` | LLM (separate call) | `qa_report.json` |

```
brief.yaml → [0 ICP] → [1 Accounts + score] → [2 Contacts] → [3 Research brief w/ sources]
          → [4 Email draft] → [5 QA: claim-check vs. sources] → runs/<ts>/ (+ failures.log)
```

## Stack
- Python 3.11, Pydantic, `httpx`, and a thin provider adapter for OpenAI Responses API or Anthropic
- `LLM_PROVIDER=openai` uses OpenAI's built-in web search; `LLM_PROVIDER=openrouter` uses OpenRouter's server-side `openrouter:web_search` tool; `LLM_PROVIDER=anthropic` uses its web-search tool
- Optional Apollo/Hunter keys are read from `.env`; no key is silently substituted with made-up enrichment

## Run
```bash
copy .env.example .env  # then set an API key for the selected LLM_PROVIDER
pip install -r requirements.txt
make run
# or: python agent/run.py --brief brief.yaml --max-accounts 8 --contacts-per-account 2
# outputs: runs/<timestamp>/{accounts.csv,contacts.csv,research/,emails/,failures.log}
```

## Design principles
1. **Source-or-silence:** no URL, no claim. Unsourced facts are dropped, not guessed.
2. **Never invent people:** if a contact isn't found, output `NOT_FOUND` with the role to look for.
3. **Scored ICP fit, not vibes:** accounts get a 0-100 score against `docs/ICP.md`.
4. **Separate generator and checker:** the QA stage re-verifies every claim in each email.
5. **Failures are logged, not hidden:** see `docs/FAILURES_AND_FIXES.md`.

## Current implementation status

See [`docs/IMPLEMENTATION_STATUS.md`](docs/IMPLEMENTATION_STATUS.md) for the implemented architecture, validation safeguards, provider configuration, live-run evidence, and the current OpenRouter credit blocker.

## Repo layout
```
README.md
brief.yaml
prompts/   00_icp_model.md … 05_email_qa.md
docs/      ICP.md  STRATEGY.md  WALKTHROUGH_SCRIPT.md  FAILURES_AND_FIXES.md
agent/     run.py (orchestrator)  tools.py  schemas.py
runs/      <timestamp>/ (real outputs, committed)
```
