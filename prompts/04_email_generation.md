# Stage 4: Personalized Email Generation

**Input:** contact row, account research brief, `brief.yaml`
**Output:** one email per contact (subject + body + `evidence` list)

## Voice
Peer-to-peer, plain, specific, brief. Sounds like a person who read about their operation and has one relevant idea. Not a pitch deck.

## Structure (body ≤ 110 words)
1. **Hook (1-2 sentences):** one specific, recent, sourced fact about THEIR company/site, relevant to the persona
2. **Bridge (1 sentence):** why that fact creates a problem or opening around inspection/safety/ops
3. **Proof (1 sentence):** relevant FlytBase customer (e.g., Anglo American for mining; Shell for hazardous/remote) stated factually, no inflated claims
4. **Ask (1 sentence):** low-friction, one question or 15-min call. No calendar links dumps.

## Persona tuning
- **Ops:** inspection cycle time, contractor scheduling/cost, uptime
- **HSE:** people out of hazard zones, exposure reduction, audit-ready records
- **Site Director:** site-wide visibility, 24/7 coverage, cost per inspection

## Language
Write in the language most likely preferred (Spanish for Chile/Peru/Argentina/Mexico, Portuguese for Brazil) unless the contact is clearly international/English-working. Output an English translation line for reviewers.

## Hard rules
- Use ONLY `FACT` items from the research brief. Every claim goes in `evidence` with its URL.
- No placeholders (`{first_name}`, `[Company]`). No identical sentences across emails except the sign-off.
- Banned: "I hope this email finds you well", "revolutionary", "game-changing", "synergy", "leverage" (as verb), "touch base", fake familiarity, fake urgency.
- Don't claim FlytBase works with a company unless it's in `flytbase_proof`.
- Don't claim savings numbers unless sourced.
- Subject ≤ 7 words, no clickbait, no "Re:" tricks.

## Output
```json
{
  "contact": "", "company": "", "language": "",
  "subject": "", "body": "", "english_translation": "",
  "evidence": [{"claim_in_email": "", "source_url": "", "source_date": ""}],
  "persona": "Ops|HSE|Site", "hook_type": "news|expansion|ops_footprint|tech_signal"
}
```
