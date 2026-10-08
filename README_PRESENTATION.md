# FlytBase BDR Agent

## Turn a campaign brief into outbound-ready research

The FlytBase BDR Agent is a research and personalization workflow for identifying relevant mining accounts, finding appropriate decision-makers, creating account briefs, and drafting evidence-backed outreach.

It is designed for large-scale lithium, copper, and iron ore operations in Latin America, with a focus on Operations, HSE, and Site leadership.

---

## The problem it solves

Outbound outreach is often generic because the work required to understand each account is slow:

- Which companies are actually a strong fit?
- Who is the right operations or safety leader?
- What recent operational signal makes outreach timely?
- Can every statement in an email be checked?

This workflow turns those questions into one repeatable, auditable process.

---

## What it produces

Starting from one campaign brief, the agent produces:

```text
ICP profile
    ↓
Ranked target accounts
    ↓
Publicly sourced contacts
    ↓
Account research briefs
    ↓
Personalized outreach drafts
    ↓
Quality-assurance results
```

Each run writes a timestamped folder so the campaign output can be reviewed later.

---

## Core features

### 1. ICP modeling

The workflow begins with SQM as the reference account. It builds a practical target-account rubric around operational scale, hazardous operating conditions, geography, commodity fit, technology signals, contractor dependence, and expansion activity.

The result is not a generic industry profile. It is a reusable scoring guide for identifying companies that resemble the target operating environment.

### 2. Account identification and prioritization

Potential accounts are evaluated against the ICP rubric and grouped into practical tiers.

For every retained account, the output includes:

- company and parent;
- country, operating sites, and commodity;
- ICP score and score breakdown;
- sourced fit reasoning;
- comparison with the reference account; and
- risk flags that may affect outreach.

Low-fit accounts are excluded instead of being forced into the list.

### 3. Contact discovery with honest uncertainty

The workflow searches for Operations, HSE, and Site leadership through public, permitted sources.

It never invents people or silently guesses contact details.

When a named leader cannot be confirmed, the output uses `NOT_FOUND` and records the exact role that should be researched next. When an email cannot be verified, it is marked clearly rather than presented as fact.

### 4. Account research briefs

Each selected account receives a structured research brief covering:

1. operating snapshot;
2. recent news;
3. operational footprint;
4. technology and expansion signals;
5. contractor dependence;
6. the most relevant inspection angle;
7. persona-specific hooks; and
8. research gaps.

Every factual statement is labeled `FACT` and paired with a source. Reasoned recommendations are labeled `INFERENCE` so there is no confusion between evidence and interpretation.

### 5. Personalized email generation

The agent creates concise, role-aware outreach for real contacts.

Each email is designed to include:

- one recent, company-specific hook;
- a relevant operational or safety bridge;
- one permitted FlytBase proof point;
- a low-friction question or meeting request; and
- an English translation when the outreach is written in Spanish or Portuguese.

The draft also includes an evidence list that maps each claim to its source.

### 6. Separate quality gate

Email drafting and email checking are separate steps.

The quality gate reviews:

- claim-to-source traceability;
- account-specific personalization;
- tone and banned phrases;
- length and call-to-action structure;
- persona fit; and
- likely reply quality.

If an email fails, it can be rewritten up to two times. A persistent failure is recorded for review instead of being hidden.

---

## Quality principles

### Source or silence

If a fact does not have a source, it does not belong in the outreach.

### No invented contacts

An unknown contact remains unknown. The workflow records `NOT_FOUND` rather than filling a row with a plausible-looking name.

### Clear distinction between fact and inference

Research briefs show what is known and what is merely a reasonable interpretation.

### Auditable outreach

The source URLs used for research are retained with the run output so a reviewer can trace the origin of an email claim.

### Visible failures

Unavailable data, empty searches, rate limits, quality failures, and missing contacts are logged. The workflow does not disguise incomplete research as completed work.

---

## How a campaign run works

### Step 1: Define the campaign

The campaign brief states the vertical, reference account, buyer personas, outreach objective, and allowed proof points.

### Step 2: Build the ICP

The agent researches the reference operation and converts the result into a weighted target-account rubric.

### Step 3: Find and score accounts

The agent identifies companies matching the ICP and prioritizes the strongest candidates.

### Step 4: Find decision-makers

The agent searches for current Operations, HSE, and Site leaders using public sources. Missing people are reported explicitly.

### Step 5: Create account context

The agent prepares a brief with recent operational signals, expansion activity, safety considerations, and persona-specific hooks.

### Step 6: Draft and check outreach

The agent writes a short outreach draft grounded only in the research brief, then independently checks it before accepting it.

---

## What a reviewer can inspect

```text
runs/<timestamp>/
├── icp_profile.json       ICP signals and sourced reference-account profile
├── accounts.json / .csv   Prioritized accounts and fit reasoning
├── contacts.csv           Confirmed contacts or explicit NOT_FOUND rows
├── research/              Account briefs with FACT and INFERENCE labels
├── emails/                Accepted personalized email drafts
├── emails.json            Structured email records and evidence maps
├── qa_report.json         Quality-gate decisions
├── trace.jsonl            Research queries and source URLs
└── failures.log           Real issues that require follow-up
```

This makes the workflow easy to demonstrate: start with the brief, open an account score, inspect a research brief, then show the source mapping for an email.

---

## Example walkthrough narrative

> “I start with the target brief and use the reference operation to define what a strong-fit mining account looks like. The system ranks target accounts using sourced operational signals, looks for the right public leadership contacts, and creates a research brief that separates facts from interpretation. It then drafts outreach from those facts only and runs an independent quality check before accepting a message. If a source, person, or email cannot be verified, the output says so clearly.”

---

## Limits to communicate clearly

- A contact may not be publicly discoverable; `NOT_FOUND` is a valid outcome.
- A contact email may remain unavailable without a verification source.
- Strong personalization depends on the amount and freshness of public operational information.
- A failed research or quality step remains visible in the run record for follow-up.

These are deliberate safeguards: the workflow prefers an honest gap over an unsupported claim.

---

## Success looks like this

- Prioritized mining accounts with clear fit reasoning.
- Relevant Operations, HSE, or Site contacts where publicly verifiable.
- Research briefs that distinguish evidence from interpretation.
- Short, role-specific outreach with claim-level source mapping.
- A visible quality decision for every drafted email.
- A record of genuine gaps and failures that can improve the next run.

---

## One-sentence summary

**The FlytBase BDR Agent turns a campaign brief into a traceable account-research and personalized-outreach workflow, while refusing to fill research gaps with invented data.**
