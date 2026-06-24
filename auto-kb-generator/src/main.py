import os
from dotenv import load_dotenv
from mistralai.client import Mistral
from slugify import slugify
from pdf_reader import read_pdf
from chunker import split_text

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

def main():
    brand = "Mercedes-Benz"
    model = "A"
    year = '2020'
    pdf_path = "input/Mercedes-Benz-A-Class_2020_EN-US_US_963552be46.pdf"

    full_text = read_pdf(pdf_path)
    chunks = split_text(full_text)

    topics = [
        {
            "title": "Check Engine",
            "slug": "check-engine",
            "problem": "Горит Check Engine"
        },
        {
            "title": "Oil Pressure Warning",
            "slug": "oil-pressure-warning",
            "problem": "Горит предупреждение давления масла"
        },
        {
            "title": "Engine Overheating",
            "slug": "engine-overheating",
            "problem": "Перегрев двигателя"
        }
    ]

    for topic in topics:
        prompt = f"""
    Ты создаешь markdown статью для авто-помощника.

    Автомобиль:
    brand: {brand}
    model: {model}
    year: {year}

    Тема:
    title: {topic["title"]}
    slug: {topic["slug"]}
    problem: {topic["problem"]}

    Текст мануала:
    {full_text[:30000]}

    Сделай статью в формате:

    ---
    title: "{topic["title"]}"
    slug: "{topic["slug"]}"
    brand: "{brand.lower()}"
    model: "{model.lower()}"
    year: "{year}"
    problem: "{topic["problem"]}"
    sourceType: "pdf-manual"
    ---

    # {topic["title"]}

    ## Что это значит

    ## Можно ли ехать

    ## Срочность

    ## Возможные причины

    ## Что проверить самому

    ## Что нельзя делать

    ## Когда ехать в сервис

    ## Краткий вывод

    Правила:
    - Пиши на русском.
    - Не выдумывай факты.
    - Если в мануале нет точной причины, так и пиши.
    - Стиль простой, для обычного водителя.
    """

    article = ask_ai(prompt)
    save_article(brand, model, year, topic["slug"], article)

if __name__ == "__main__":
    main()