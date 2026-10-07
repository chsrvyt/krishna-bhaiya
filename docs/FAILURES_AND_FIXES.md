# Failures and Fixes (fill in from REAL runs; do not pre-write)

The assignment asks to show where the agent failed and how to fix it. Copy real entries from `runs/<ts>/failures.log` here after your actual run.

| # | Stage | What happened (real) | Root cause | Fix (implemented / proposed) |
|---|---|---|---|---|
| 1 | Stage 0 / OpenAI web-search call | The configured OpenAI request returned HTTP 429 `insufficient_quota` / `credit_balance_exhausted`; no ICP artifact was generated. | The OpenAI project has no API credits, as returned by the provider during the run. | Implemented retry/backoff for transient provider errors while failing quota exhaustion immediately. Add API credits or configure a funded supported provider, then rerun. |
| 2 | Stage 0 / OpenRouter startup | The OpenRouter Stage 0 attempt stopped before a network call because `OPENROUTER_API_KEY` is absent from `.env`. | The existing environment is configured only with `OPENAI_API_KEY`. | Added OpenRouter variables and a tool-capable default model to `.env.example`. Set `LLM_PROVIDER=openrouter` and a valid `OPENROUTER_API_KEY`, then rerun. |
| 3 | Stage 0 / OpenRouter live call | After the code fixes, OpenRouter returned HTTP 402: “This account never purchased credits.” No web search or ICP artifact could be produced. | The configured OpenRouter account has no billable API credit balance. | Purchase credits or use a funded key/account, then rerun Stage 0. The agent logs the provider failure and does not fabricate output. |

## Common failure modes to watch for (and planned fixes)
| Failure | Likely cause | Fix |
|---|---|---|
| Contact not found for an account | Leadership pages are sparse; titles in Spanish | Add Spanish/Portuguese title queries; fall back to annual-report/sustainability-report names; output `NOT_FOUND` |
| Stale titles | Job changes, old press releases | 18-month recency rule; cross-check LinkedIn snippet date |
| Email not verifiable | No paid enrichment | Label `pattern_guess`; verify via Hunter/NeverBounce; or contact via LinkedIn first |
| Hallucinated claim in email | LLM fills gaps | QA gate + source-or-silence; auto-reject and regenerate |
| Rate limits / timeouts | API/search throttling | Retry with backoff, cache, batch by account |
| Generic emails across accounts | Research too thin | Raise research depth requirement; fail QA on swap test |
| Wrong persona/title match | Ambiguous titles (e.g., "Gerente de Operaciones") | Add title mapping table and seniority scoring |
