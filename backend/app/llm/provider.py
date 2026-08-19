from __future__ import annotations

import os
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI

from .base import LLMProvider

load_dotenv()


class GrokProvider(LLMProvider):
    def __init__(self) -> None:
        api_key = os.getenv("XAI_API_KEY")

        if not api_key:
            raise RuntimeError(
                "XAI_API_KEY is not configured."
            )

        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.x.ai/v1",
        )

        self.model = os.getenv(
            "XAI_MODEL",
            "grok-4.5",
        )

    def generate(
        self,
        messages: list[dict[str, str]],
        **kwargs: Any,
    ) -> str:

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=kwargs.get("temperature", 0.3),
            max_tokens=kwargs.get("max_tokens", 300),
        )

        content = response.choices[0].message.content

        if not content:
            raise RuntimeError(
                "Grok returned an empty response."
            )

        return content.strip()