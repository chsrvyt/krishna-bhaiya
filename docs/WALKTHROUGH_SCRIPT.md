# Walkthrough Video Script (8-12 min, screen share)

Record in Loom. Run the agent live, don't narrate a recording of something old.

| Time | Section | What to show / say |
|---|---|---|
| 0:00-0:45 | Intro + problem | "This agent turns a campaign brief into accounts, contacts, research, and emails. I'm not writing emails, the system is." Show repo + `brief.yaml`. |
| 0:45-2:30 | ICP + account identification | Open `docs/ICP.md` and `prompts/01`. Show how SQM was modeled (scale, 24/7 hazard, contractors, tech, expansion). Show `accounts.csv` with scores + sourced reasoning for 2 accounts. |
| 2:30-4:15 | Contact discovery + enrichment | Show `prompts/02`, run Stage 2 live. Point at `email_status` and `NOT_FOUND` rows: "it never invents people." |
| 4:15-5:30 | Research brief | Open one `research/<account>.md`. Show FACT vs INFERENCE labels and source URLs. |
| 5:30-8:00 | LIVE email generation | Run `python agent/run.py` for ≥3 real contacts at ≥2 companies. Show output files appear. Show QA gate pass/fail. |
| 8:00-9:30 | One email deep dive | Pick one email. Highlight: the signal used, source URL, persona tuning, why Anglo American/Shell proof was chosen, why it can't be sent to another company. |
| 9:30-10:30 | Design decision I'm proud of | Source-or-silence + separate QA checker: unsupported claims are blocked before a human sees them. |
| 10:30-11:30 | Failures + limitation | Show `failures.log`/a real failure (e.g., contact not found, rate limit, stale title). Explain fix. Limitation: no paid enrichment (Apollo/ZoomInfo/Sales Nav) → emails often `pattern_guess`; with budget, verified emails + job-change webhooks. |
| 11:30-12:00 | Close | Sequence + metrics in one sentence, point to `STRATEGY.md`. |

## Tips
- Keep terminal font large; pre-open files in tabs.
- Do one dry run first, then record.
- If something fails live, leave it in and explain; the brief explicitly rewards that.
