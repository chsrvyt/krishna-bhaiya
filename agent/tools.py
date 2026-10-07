"""Auditable network helpers. Every request is cached and traced."""
from __future__ import annotations
import asyncio, json, re
from datetime import datetime, timezone
from pathlib import Path
import httpx


class RunLogger:
    def __init__(self, run_dir: Path):
        self.run_dir = run_dir
        self.trace_path = run_dir / "trace.jsonl"
        self.failure_path = run_dir / "failures.log"
        self.json_path = run_dir / "events.jsonl"
        self._lock = asyncio.Lock()

    async def trace(self, **event: object) -> None:
        event.update(timestamp=datetime.now(timezone.utc).isoformat())
        async with self._lock:
            with self.trace_path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(event, ensure_ascii=False) + "\n")

    async def event(self, **event: object) -> None:
        event.update(timestamp=datetime.now(timezone.utc).isoformat())
        async with self._lock:
            with self.json_path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(event, ensure_ascii=False) + "\n")

    async def failure(self, stage: str, input_value: object, error: str, suggested_fix: str) -> None:
        row = {"stage": stage, "input": input_value, "error": self._redact(error), "suggested_fix": suggested_fix,
               "timestamp": datetime.now(timezone.utc).isoformat()}
        async with self._lock:
            with self.failure_path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
        await self.event(kind="failure", **row)

    @staticmethod
    def _redact(message: str) -> str:
        """Do not persist bearer material or provider key-management URLs."""
        message = re.sub(r"(/keys/)[^/?'\"\\s]+", r"\1<redacted>", message)
        message = re.sub(r"(?i)(bearer\\s+)[^\\s'\"]+", r"\1<redacted>", message)
        return re.sub(r"user_[A-Za-z0-9_-]+", "<redacted-user-id>", message)


class WebCache:
    def __init__(self, logger: RunLogger):
        self.logger, self.cache = logger, {}

    async def fetch(self, url: str) -> str:
        key = f"fetch:{url}"
        if key in self.cache:
            return self.cache[key]
        try:
            async with httpx.AsyncClient(follow_redirects=True, timeout=20, headers={"User-Agent": "FlytBaseBDRAgent/1.0"}) as client:
                response = await client.get(url)
                response.raise_for_status()
                text = re.sub(r"\s+", " ", response.text)[:100_000]
            self.cache[key] = text
            await self.logger.trace(kind="fetch", url=url, status="ok")
            return text
        except Exception as exc:
            await self.logger.failure("web_fetch", url, str(exc), "Verify URL or retry after network/rate-limit delay.")
            raise
