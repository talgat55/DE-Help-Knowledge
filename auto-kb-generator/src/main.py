import os
import json
from pathlib import Path
from dotenv import load_dotenv
from mistralai.client import Mistral
from pdf_reader import read_pdf
from chunker import split_text
from storage import save_text, save_json, load_json
from ai_client import chat_complete
from topic_extractor import extract_topics_from_chunks
from logger import PipelineLogger
from config import load_config

config = load_config()

MODEL_NAME = config["model"]["name"]
TEMPERATURE = config["model"]["temperature"]

INPUT_DIR = config["paths"]["input_dir"]
OUTPUT_DIR = config["paths"]["output_dir"]

MAX_TOPICS = config["generation"]["max_topics"]
MAX_ARTICLES = config["generation"]["max_articles"]

CHUNK_SIZE = config["chunks"]["chunk_size"]
RELEVANT_CHUNKS_LIMIT = config["chunks"]["relevant_chunks_limit"]
PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOGS_DIR = config["paths"]["logs_dir"]

load_dotenv()
logger = PipelineLogger(LOGS_DIR)
client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"), timeout_ms=180_000)

def ask_ai(prompt: str) -> str:
    response = chat_complete(
        client,
        model=MODEL_NAME,
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=TEMPERATURE
    )

    return response.choices[0].message.content

def save_article(brand, model, year, slug, content, logger):
    folder = f"{OUTPUT_DIR}/{brand.lower()}/{model.lower().replace(' ', '-')}/{year}"
    os.makedirs(folder, exist_ok=True)

    path = f"{folder}/{slug}.md"
    if os.path.exists(path):
        logger.log(f"Skip exists: {path}")
        return

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

    logger.log(f"Saved: {path}")

def save_topics(brand, model, year, topics):
    folder = f"output/{brand.lower()}/{model.lower().replace(' ', '-')}/{year}"
    os.makedirs(folder, exist_ok=True)

    path = f"{folder}/topics.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(topics, f, ensure_ascii=False, indent=2)

    logger.log(f"Topics saved: {len(topics)}")


def main():
    brand = "Mercedes-Benz"
    model = "A"
    year = '2020'
    pdf_path = "input/Mercedes-Benz-A-Class_2020_EN-US_US_963552be46.pdf"

    full_text = read_pdf(pdf_path)
    chunks = split_text(full_text, chunk_size=CHUNK_SIZE)
    base_name = f"{brand.lower()}_{model.lower().replace(' ', '_')}_{year}"
    save_text(f"data/bronze/{base_name}_raw.txt", full_text)
    save_json(f"data/silver/{base_name}_chunks.json", chunks)

    topics_path = f"data/silver/{base_name}_topics.json"
    if os.path.exists(topics_path):
        topics = load_json(topics_path)
        logger.log(f"Loaded cached topics: {topics_path}")
    else:
        max_chunks = int(os.getenv("MAX_CHUNKS_FOR_TOPICS", "3"))
        topics = extract_topics_from_chunks(
            client=client,
            chunks=chunks,
            brand=brand,
            model=model,
            year=year,
            max_chunks=max_chunks,
        )
        save_json(topics_path, topics)

    save_topics(brand, model, year, topics)

    article_template = (PROJECT_ROOT / "prompts" / "generate_article.txt").read_text(encoding="utf-8")

    for topic in topics[:MAX_ARTICLES]:
        prompt = article_template.format(
            brand=brand,
            model=model,
            year=year,
            title=topic["title"],
            problem=topic["problem"],
            slug=topic["slug"],
        )
        prompt += f"\n\nТекст мануала:\n{full_text[:12000]}\n"

        article = ask_ai(prompt)
        save_article(brand, model, year, topic["slug"], article, logger=logger)

if __name__ == "__main__":
    main()