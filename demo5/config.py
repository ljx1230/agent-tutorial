from __future__ import annotations

from pathlib import Path


API_URL = "https://api.deepseek.com/chat/completions"
MODEL_NAME = "deepseek-v4-flash"
MAX_HISTORY_TURNS = 6
MAX_AGENT_LOOPS = 8
MAX_COMPLETION_TOKENS = 3000
GENERATED_FILES_DIR = Path(__file__).resolve().parent / "generated_files"
