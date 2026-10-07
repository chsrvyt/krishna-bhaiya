"""Small provider adapter. Prompts are supplied by stages from disk."""
from __future__ import annotations
import asyncio, json, os, re
from typing import TypeVar, Type
from anthropic import Anthropic
from openai import OpenAI
from pydantic import BaseModel, ValidationError
from .tools import RunLogger

T = TypeVar("T", bound=BaseModel)


class LLM:
    def __init__(self, logger: RunLogger):
        self.logger = logger
        self.provider = os.getenv("LLM_PROVIDER", "openai").lower()
        if self.provider == "openai":
            key = os.getenv("OPENAI_API_KEY")
            if not key:
                raise RuntimeError("OPENAI_API_KEY is missing; create .env from .env.example")
            self.client, self.model = OpenAI(api_key=key), os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
        elif self.provider == "openrouter":
            key = os.getenv("OPENROUTER_API_KEY")
            if not key:
                raise RuntimeError("OPENROUTER_API_KEY is missing; create .env from .env.example")
            base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
            self.client = OpenAI(api_key=key, base_url=base_url)
            self.model = os.getenv("OPENROUTER_MODEL", "openai/gpt-4.1-mini")
            self.max_tokens = int(os.getenv("OPENROUTER_MAX_TOKENS", "1000"))
        elif self.provider == "anthropic":
            key = os.getenv("ANTHROPIC_API_KEY")
            if not key:
                raise RuntimeError("ANTHROPIC_API_KEY is missing; create .env from .env.example")
            self.client, self.model = Anthropic(api_key=key), os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")
        else:
            raise RuntimeError("LLM_PROVIDER must be openai, openrouter, or anthropic")

    async def structured(self, stage: str, prompt: str, schema: Type[T], web_search: bool = False) -> T:
        error = ""
        for attempt in range(2):
            suffix = "\nReturn JSON only, matching this schema exactly:\n" + json.dumps(schema.model_json_schema())
            if error:
                suffix += "\nYour previous JSON failed validation. Correct it: " + error
            try:
                if web_search:
                    await self.logger.trace(kind="search_request", stage=stage, query=prompt)
                raw = await self._call_with_backoff(stage, prompt + suffix, web_search)
                await self.logger.event(kind="llm", stage=stage, provider=self.provider, web_search=web_search)
                value = schema.model_validate_json(_json_payload(raw))
                await self.logger.trace(kind="llm_result", stage=stage, source_urls=_urls(value.model_dump()))
                return value
            except ValidationError as exc:
                error = str(exc)
                await self.logger.failure(stage, "structured output", error, "Schema retry was requested from the model.")
            except Exception as exc:
                await self.logger.failure(stage, "LLM call", str(exc), "Check API key, quota, model access, or retry after backoff.")
                raise
        raise RuntimeError(f"{stage}: invalid structured output after retry")

    async def _call_with_backoff(self, stage: str, prompt: str, web_search: bool) -> str:
        """Retry only network/rate-limit failures; never burn requests on exhausted quota."""
        for attempt in range(3):
            try:
                return await asyncio.to_thread(self._call, prompt, web_search)
            except Exception as exc:
                message = str(exc).lower()
                exhausted = "insufficient_quota" in message or "credit_balance_exhausted" in message
                retryable = "429" in message or "rate limit" in message or "timeout" in message or "connection" in message
                if exhausted or not retryable or attempt == 2:
                    raise
                delay = 2 ** attempt
                await self.logger.failure(stage, "provider request", str(exc), f"Transient provider failure; retrying in {delay}s.")
                await asyncio.sleep(delay)

    def _call(self, prompt: str, web_search: bool) -> str:
        if self.provider == "openai":
            tools = [{"type": "web_search_preview"}] if web_search else []
            response = self.client.responses.create(model=self.model, input=prompt, tools=tools)
            return response.output_text
        if self.provider == "openrouter":
            # OpenRouter executes this server-side tool loop. It is not a client-side
            # mock or a plugin; the final message is grounded in the returned search.
            tools = ([{"type": "openrouter:web_search", "parameters": {"max_results": 5, "max_total_results": 15}}]
                     if web_search else [])
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                tools=tools,
                max_tokens=self.max_tokens,
            )
            content = response.choices[0].message.content
            if not content:
                raise RuntimeError("OpenRouter returned no final content after server tool execution")
            return content
        tools = [{"type": "web_search_20250305", "name": "web_search"}] if web_search else []
        response = self.client.messages.create(model=self.model, max_tokens=5000, tools=tools, messages=[{"role": "user", "content": prompt}])
        return "".join(block.text for block in response.content if hasattr(block, "text"))


def _urls(value: object) -> list[str]:
    found: list[str] = []
    def walk(item: object) -> None:
        if isinstance(item, dict):
            for k, v in item.items():
                if k.endswith("url") and isinstance(v, str) and v.startswith("http"):
                    found.append(v)
                walk(v)
        elif isinstance(item, list):
            for child in item: walk(child)
    walk(value)
    return sorted(set(found))


def _json_payload(raw: str) -> str:
    """Accept a model's common Markdown JSON fence without weakening validation."""
    fenced = re.fullmatch(r"\s*```(?:json)?\s*\n?(.*?)\n?```\s*", raw, flags=re.DOTALL | re.IGNORECASE)
    return fenced.group(1).strip() if fenced else raw.strip()
