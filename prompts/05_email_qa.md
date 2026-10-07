# Stage 5: Email QA Gate (separate LLM call)

**Input:** email JSON + research brief
**Task:** Act as a skeptical mining ops director and a compliance checker.

Check:
1. **Claim verification:** every factual claim in the email maps to a `FACT` in the brief with a URL. Flag unsupported claims.
2. **Personalization:** could this email be sent to another company by swapping the name? If yes → FAIL.
3. **Human tone:** flag buzzwords, AI-isms ("delve", "in today's fast-paced"), excessive flattery.
4. **Length/structure:** ≤ 110 words, one ask.
5. **Proof accuracy:** FlytBase customer references match the allowed list.
6. **Persona fit:** hook matches the contact's role.
7. **Reply likelihood (1-5)** with a one-line reason.

**Output:**
```json
{"pass": true, "issues": [""], "unsupported_claims": [""], "personalization_score": 1, "tone_score": 1, "reply_likelihood": 1, "suggested_fix": ""}
```
**Loop:** if `pass=false`, send issues back to Stage 4 for one rewrite (max 2 retries), then log to `failures.log` if still failing.
