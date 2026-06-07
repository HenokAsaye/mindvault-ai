from __future__ import annotations

from typing import AsyncGenerator

import google.generativeai as genai

from app.domain.ports.outbound.llm_port import LLMPort


class GeminiAdapter(LLMPort):
    def __init__(self, api_key: str, model: str = "gemini-2.0-flash") -> None:
        genai.configure(api_key=api_key)
        self._model = model

    async def generate_response_stream(
        self,
        *,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
    ) -> AsyncGenerator[str, None]:
        system_prompt = None
        contents = []
        for m in messages:
            if m["role"] == "system":
                system_prompt = m["content"]
            else:
                role = "user" if m["role"] == "user" else "model"
                contents.append({"role": role, "parts": [{"text": m["content"]}]})

        model = genai.GenerativeModel(
            model_name=self._model,
            system_instruction=system_prompt,
            generation_config=genai.types.GenerationConfig(temperature=temperature),
        )

        response = await model.generate_content_async(contents, stream=True)

        async for chunk in response:
            if chunk.text:
                yield chunk.text
