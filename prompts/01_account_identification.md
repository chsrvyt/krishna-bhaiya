# Stage 1: Account Identification

**Input:** `icp_profile.json`, `brief.yaml`, `--max-accounts N`
**Tools:** web_search, web_fetch

**Task:** Find N mining companies/operations in Latin America that match the ICP. Prefer lithium, copper, iron ore operators with large, 24/7, hazardous open-air sites. Include at least 2 different countries and 2 commodities if possible.

For each candidate:
- Company, parent, country, key site(s), commodity
- Score 0-100 against the rubric, with per-criterion sub-scores
- **Fit reasoning:** 2-4 sentences, each tied to a source URL (with publication date)
- Similarity to SQM (what's the same, what's different)
- Risk flags (e.g., existing drone vendor, state-owned procurement rules, recent layoffs)

**Output (JSON array):**
```json
{
  "company": "", "parent": "", "country": "", "sites": [""], "commodity": "",
  "icp_score": 0, "score_breakdown": {"scale":0,"hazard_24x7":0,"contractor":0,"geo":0,"commodity":0,"tech":0,"expansion":0},
  "fit_reasoning": [{"point": "", "source_url": "", "source_date": ""}],
  "sqm_similarity": "", "risk_flags": [""], "tier": "A|B|exclude"
}
```
**Rules:**
- Only include companies with at least 3 sourced signals.
- Do not invent sites, production numbers, or projects. Unknown → omit.
- Sort by score desc. Drop anything < 60.
- Exclude SQM itself (it is the reference).
