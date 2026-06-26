from datetime import datetime
from pathlib import Path

class PipelineLogger:
    def __init__(self, logs_dir: str = "logs") :
        Path(logs_dir).mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.log_path = Path(logs_dir) / f"run_{timestamp}.log"

    def log(self, message: str):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{now}] {message}"

        print(line)

        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(line + "\n")