# Implementation Status

## What was built

The repository has been normalized into the documented layout:

```text
README.md                 Setup and run instructions
brief.yaml                Campaign input
prompts/00...05.md        Runtime-loaded stage instructions
docs/                     ICP, strategy, walkthrough, failures, this status
agent/run.py              CLI orchestration and artifact writing
agent/llm.py              OpenAI, OpenRouter, and Anthropic provider adapter
agent/tools.py            Run event, trace, failure logging, and fetch cache
agent/schemas.py          Pydantic contracts for stage outputs
agent/stages/             One module for every pipeline stage
agent/qa.py               Deterministic email guardrails
tests/                    Offline schema/provider/guardrail tests
```

`brief.yaml`, the prompts, and the supplied strategy documents were preserved as the source of truth. Each stage module loads its corresponding file from `prompts/` at runtime; no prompt text is embedded in Python.

## Pipeline implementation

| Stage | Implementation | Artifact on successful run |
|---|---|---|
| 0: ICP | Live provider web search plus Pydantic validation. The fixed scoring rubric is parsed from `docs/ICP.md` at runtime. | `icp_profile.json` |
| 1: Accounts | Live web-search model call, source-bearing fit reasons, score/tier filtering, JSON and CSV writers. | `accounts.json`, `accounts.csv` |
| 2: Contacts | Live public-source discovery for Ops, HSE, and Site roles; `NOT_FOUND` remains valid output. | `contacts.csv` |
| 3: Research | Per-account Markdown research brief through live search. | `research/<account>.md` |
| 4: Email | Per-contact draft grounded in the research brief. | `emails/<contact>.md`, `emails.json` |
| 5: QA | A separate model call plus deterministic checks; up to two rewrites. | `qa_report.json` |

Account research tasks are concurrency-limited with `--concurrency`. Every live-search prompt and every source URL returned in structured output is written to `trace.jsonl`. Console progress is concise; `events.jsonl` retains full run events.

## Provider support

The provider adapter supports:

| `LLM_PROVIDER` | Credentials | Live-search mechanism |
|---|---|---|
| `openai` | `OPENAI_API_KEY` | OpenAI Responses API `web_search_preview` |
| `openrouter` | `OPENROUTER_API_KEY` | OpenAI-compatible client at `OPENROUTER_BASE_URL` with OpenRouter server tool `openrouter:web_search` |
| `anthropic` | `ANTHROPIC_API_KEY` | Anthropic web-search tool |

OpenRouter configuration is documented in `.env.example`:

```dotenv
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_MODEL=openai/gpt-4.1-mini
OPENROUTER_MAX_TOKENS=1000
```

`OPENROUTER_MAX_TOKENS` is explicit because OpenRouter otherwise reserves the selected model's much larger default maximum, which can exceed a restricted key's limit before a request starts. The default is intentionally small for Stage 0; it can be raised after the account has adequate credit.

## Guardrails and auditability

- No data is generated when a provider/search request fails. Failures are logged and the run stops safely.
- Pydantic validates all structured stage outputs. A validation failure triggers one corrected-output retry.
- Markdown-fenced JSON is normalized before validation; this accepts presentation formatting without accepting invalid JSON.
- Contacts require a real two-part name or `NOT_FOUND`; `not_found` contacts cannot carry an email.
- Email checks enforce word limits, banned phrases, placeholder detection, allowed FlytBase proof names, evidence presence, and a company/contact swap test.
- Provider failure text is redacted before it is saved to avoid recording bearer credentials or provider key-management identifiers.
- `.env` is ignored by Git and is never printed by the agent.

## Tests

The offline suite does not call the network. It covers:

- source URL schema validation;
- banned phrase and placeholder detection;
- generic-email swap testing;
- `NOT_FOUND` contact rules;
- OpenRouter client/base URL/token-budget configuration;
- fenced JSON normalization;
- JSON artifact writing;
- parsing the required seven-item ICP rubric from the canonical document.

Latest local result: `9 passed`.

## Live-run evidence

| Run | Result |
|---|---|
| `runs/20261008T030644` | Identified OpenRouter's implicit 65,536-token request reservation. |
| `runs/20261008T031146` | Live web research completed; surfaced a fenced-JSON and artifact-writer defect. |
| `runs/20261008T031411` | Created a live-source ICP artifact, then it was superseded because its rubric did not match `docs/ICP.md` exactly. |
| `runs/20261008T031950` | Final corrected code reached OpenRouter but received definitive HTTP 402 due to the account having no purchased credits. |

The corresponding `failures.log`, `events.jsonl`, and `trace.jsonl` files are retained in each run folder. `docs/FAILURES_AND_FIXES.md` contains only real observed failures.

## Remaining issue

The current OpenRouter account/key has no billable API credit balance. The provider's final response was HTTP 402, stating that the account had never purchased credits. This prevents any provider request, web search, or fresh Stage 0 artifact from completing. It is an external account/billing issue rather than a local code issue.

No mock ICP, accounts, contacts, research, emails, or sources were written to work around this block.

## Resume instructions

1. Fund the configured OpenRouter account or replace the key with one on a funded account.
2. Confirm `.env` has the OpenRouter variables above.
3. Run the small live proof:

   ```powershell
   python agent/run.py --brief brief.yaml --max-accounts 2 --contacts-per-account 1 --only-stage 0
   ```

4. Inspect the resulting `runs/<timestamp>/icp_profile.json`, `trace.jsonl`, and `failures.log`.
5. When Stage 0 succeeds, run the complete pipeline:

   ```powershell
   python agent/run.py --brief brief.yaml --max-accounts 3 --contacts-per-account 1
   ```

The full run should be attempted only with enough provider budget for multiple web-search and QA calls. Any future real failure is automatically retained in that run's `failures.log`.
