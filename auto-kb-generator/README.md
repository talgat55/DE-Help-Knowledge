# Auto KB Generator

ETL-пайплайн для преобразования PDF-мануалов автомобилей в статьи базы знаний с помощью Mistral AI.

## Архитектура

```
PDF (input/)
  │
  ▼
Bronze  — сырой текст          data/bronze/{brand}_{model}_{year}_raw.txt
  │
  ▼
Silver  — чанки и топики       data/silver/{brand}_{model}_{year}_chunks.json
                               data/silver/{brand}_{model}_{year}_topics.json
  │
  ▼
Gold    — готовые статьи       articles/{brand}/{model}/{year}/*.md
                               articles/{brand}/{model}/{year}/topics.json
```

## Требования

- Python 3.12+
- API-ключ [Mistral AI](https://console.mistral.ai/)

## Установка

```bash
cd auto-kb-generator
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Укажите MISTRAL_API_KEY в .env
```

## Запуск

Положите PDF в `input/` и запустите пайплайн из корня `auto-kb-generator`:

```bash
cd src
python main.py
```

Параметры brand / model / year / pdf_path задаются в `main.py` (пока без CLI).

## Конфигурация

| Файл | Назначение |
|------|------------|
| `config.yml` | Модель, пути, лимиты чанков и статей |
| `.env` | `MISTRAL_API_KEY`, `MAX_CHUNKS_FOR_TOPICS` |
| `prompts/` | Шаблоны промптов для извлечения тем и генерации статей |

Основные параметры в `config.yml`:

- `generation.max_articles` — сколько статей генерировать за прогон
- `chunks.chunk_size` — размер чанка при разбиении текста
- `paths.output_dir` — каталог для готовых статей (`articles/`)

## Результаты прогона

- `articles/` — markdown-статьи и `topics.json`
- `logs/` — лог каждого запуска
- `stats/` — JSON со статистикой прогона

## Структура проекта

```
auto-kb-generator/
├── config.yml
├── requirements.txt
├── .env.example
├── input/          # исходные PDF (не в git)
├── data/
│   ├── bronze/
│   ├── silver/
│   └── gold/
├── articles/       # готовые статьи (gold)
├── prompts/
├── src/
│   ├── main.py
│   ├── pdf_reader.py
│   ├── chunker.py
│   ├── topic_extractor.py
│   ├── ai_client.py
│   ├── storage.py
│   ├── logger.py
│   ├── stats.py
│   └── config.py
├── logs/
└── stats/
```
