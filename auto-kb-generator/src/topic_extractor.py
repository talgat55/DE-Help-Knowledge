import json
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def clean_json_response(text: str) -> str:
    text = text.strip()
    text = re.sub(r"```(?:json)?\s*", "", text)
    text = re.sub(r"```", "", text).strip()

    start = text.find("[")
    if start == -1:
        raise ValueError("JSON array not found in AI response")

    depth = 0
    for index, char in enumerate(text[start:], start=start):
        if char == "[":
            depth += 1
        elif char == "]":
            depth -= 1
            if depth == 0:
                return text[start:index + 1]

    raise ValueError("JSON array not found in AI response")


def parse_topics_response(content: str) -> list[dict]:
    text = content.strip()
    text = re.sub(r"```(?:json)?\s*", "", text)
    text = re.sub(r"```", "", text).strip()

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        data = json.loads(clean_json_response(text))

    if isinstance(data, list):
        return data

    if isinstance(data, dict):
        for key in ("topics", "items", "data"):
            value = data.get(key)
            if isinstance(value, list):
                return value

    raise ValueError(f"Unexpected JSON structure in AI response: {text[:500]}")


def extract_topics_from_text(client, text: str, brand: str, model: str, year: str) -> list[dict]:
    prompt_path = PROJECT_ROOT / "prompts" / "extract_topics.txt"
    prompt_template = prompt_path.read_text(encoding="utf-8")

    prompt = f"""
{prompt_template}

Автомобиль:
brand: {brand}
model: {model}
year: {year}

Текст мануала:
{text[:30000]}
"""

    response = client.chat.complete(
        model="mistral-small-latest",
        messages=[
            {
                "role": "system",
                "content": "Отвечай только валидным JSON без markdown и пояснений.",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=0.2,
        response_format={"type": "json_object"},
    )

    content = response.choices[0].message.content
    return parse_topics_response(content)
