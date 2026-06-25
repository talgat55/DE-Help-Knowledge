import os
import json
from pathlib import Path
from dotenv import load_dotenv
from mistralai.client import Mistral
from pdf_reader import read_pdf
from chunker import split_text
from topic_extractor import extract_topics_from_text

PROJECT_ROOT = Path(__file__).resolve().parent.parent

load_dotenv()

client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))

def ask_ai(prompt: str) -> str:
    response = client.chat.complete(
        model="mistral-medium-latest",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )

    return response.choices[0].message.content

def save_article(brand, model, year, slug, content):
    folder = f"output/{brand.lower()}/{model.lower().replace(' ', '-')}/{year}"
    os.makedirs(folder, exist_ok=True)

    path = f"{folder}/{slug}.md"
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"Saved: {path}")

def save_topics(brand, model, year, topics):
    folder = f"output/{brand.lower()}/{model.lower().replace(' ', '-')}/{year}"
    os.makedirs(folder, exist_ok=True)

    path = f"{folder}/topics.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(topics, f, ensure_ascii=False, indent=2)

    print(f"Topics saved: {path}")


def main():
    brand = "Mercedes-Benz"
    model = "A"
    year = '2020'
    pdf_path = "input/Mercedes-Benz-A-Class_2020_EN-US_US_963552be46.pdf"

    full_text = read_pdf(pdf_path)
    #chunks = split_text(full_text)

    topics = extract_topics_from_text(
        client=client,
        text=full_text,
        brand=brand,
        model=model,
        year=year,
    )

    save_topics(brand, model, year, topics)

    article_template = (PROJECT_ROOT / "prompts" / "generate_article.txt").read_text(encoding="utf-8")

    for topic in topics:
        prompt = article_template.format(
            brand=brand,
            model=model,
            year=year,
            title=topic["title"],
            problem=topic["problem"],
            slug=topic["slug"],
        )
        prompt += f"\n\nТекст мануала:\n{full_text[:30000]}\n"

        article = ask_ai(prompt)
        save_article(brand, model, year, topic["slug"], article)

if __name__ == "__main__":
    main()