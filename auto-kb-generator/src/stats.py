import json
from datetime import datetime
from pathlib import Path

class PipelineStats:
    def __init__(self, stats_dir: str ="stats"):
        Path(stats_dir).mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.path = Path(stats_dir) / f"run{timestamp}.json"

        self.data = {
            "started_at": datetime.now().isoformat(),
            "finished_at": None,
            "pdf_files_total": 0,
            "pdf_files_processed": 0,
            "pdf_files_failed": 0,
            "topics_found": 0,
            "articles_created": 0,
            "articles_skipped": 0,
            "article_errors": 0,
            "files": []
        }

    def add_file_result(self, result: dict):
        self.data["files"].append(result)

    def finish(self):
        self.data["finished_at"] = datetime.now().isoformat()

        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent = 2)