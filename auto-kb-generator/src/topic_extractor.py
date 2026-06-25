import json
import re
from pathlib import Path

from ai_client import chat_complete

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MAX_TEXT_CHARS = 12_000


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
{text[:MAX_TEXT_CHARS]}
"""

    response = chat_complete(
        client,
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


def extract_topics_from_chunks(
    client,
    chunks: list[str],
    brand: str,
    model: str,
    year: str,
    max_chunks: int | None = None,
) -> list[dict]:
    topics_by_slug: dict[str, dict] = {}
    chunks_to_process = chunks[:max_chunks] if max_chunks else chunks

    for index, chunk in enumerate(chunks_to_process, start=1):
        print(f"Extracting topics from chunk {index}/{len(chunks_to_process)}...")
        chunk_topics = extract_topics_from_text(client, chunk, brand, model, year)

        for topic in chunk_topics:
            slug = topic.get("slug")
            if slug and slug not in topics_by_slug:
                topics_by_slug[slug] = topic

    return list(topics_by_slug.values())
