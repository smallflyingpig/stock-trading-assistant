import os
from pathlib import Path
import yaml

CONFIG_PATH = Path.home() / ".hermes" / "config.yaml"

def load_config():
    """Load LLM API config from ~/.hermes/config.yaml"""
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH) as f:
            return yaml.safe_load(f)
    return {}

class Settings:
    OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
    DASHSCOPE_API_KEY = os.environ.get("DASHSCOPE_API_KEY", "")
    # Load from hermes config if env vars not set
    config = load_config()
    if not OPENROUTER_API_KEY and config.get("llm", {}).get("openrouter_api_key"):
        OPENROUTER_API_KEY = config["llm"]["openrouter_api_key"]
    if not DASHSCOPE_API_KEY and config.get("llm", {}).get("dashscope_api_key"):
        DASHSCOPE_API_KEY = config["llm"]["dashscope_api_key"]

settings = Settings()
