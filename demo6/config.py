from __future__ import annotations

from pathlib import Path


# 第六课的配置保持尽量简单：
# - 不把这些常量塞回 runtime 里
# - 也不做复杂配置系统
# 这样读代码时，大家可以先把“会变化的环境参数”集中看完。
API_URL = "https://api.deepseek.com/chat/completions"
MODEL_NAME = "deepseek-v4-flash"
MAX_COMPLETION_TOKENS = 3000
MAX_AGENT_LOOPS = 8
MAX_HISTORY_TURNS = 6
GENERATED_FILES_DIR = Path(__file__).resolve().parent / "generated_files"
