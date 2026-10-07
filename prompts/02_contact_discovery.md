# Stage 2: Contact Discovery

**Input:** `accounts.json` (Tier A/B)
**Tools:** web_search, web_fetch, Apollo/Hunter API (optional)

**Target roles (priority order):** Head/VP/Director of Operations; VP/Head/Director of HSE (Seguridad, Salud Ocupacional / SSO / Medio Ambiente); Site/Plant/Mine Manager or Director (Gerente de Operaciones / Gerente Mina / Gerente General de Faena). Also check Spanish and Portuguese titles.

**Task:** For each account, find up to K real people currently in those roles.

**Sources allowed:** company leadership/“team” pages, annual/sustainability reports, press releases, conference speaker pages, news articles, public LinkedIn profile URLs surfaced by search, Apollo/Hunter results.

**Output (CSV):**
`company, full_name, title, seniority, role_match (Ops|HSE|Site), linkedin_url, email, email_status (verified|pattern_guess|not_found), source_url, source_date, confidence (high|med|low)`

**Rules:**
- **Never invent a person.** If no named person is found, output a row with `full_name=NOT_FOUND` and the exact title to target next. This is acceptable output.
- Never guess emails silently. Pattern-derived emails must be labeled `pattern_guess` and ideally verified via Hunter/Apollo.
- Reject anyone whose source is older than 18 months unless corroborated (people change jobs).
- Don't scrape behind LinkedIn login or violate platform ToS.
