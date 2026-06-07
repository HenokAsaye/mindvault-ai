from __future__ import annotations

from pathlib import Path

import yaml


def load_prompts() -> dict[str, str]:
    prompts_path = Path(__file__).parent / "prompts.yml"
    with open(prompts_path, "r") as f:
        data = yaml.safe_load(f)
    return data


PROMPTS = load_prompts()
SYSTEM_PROMPT_TEMPLATE = PROMPTS["system_prompt"]
