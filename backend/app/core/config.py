import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv(override=True)


def _bool_env(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    dashscope_api_key: str = os.getenv("DASHSCOPE_API_KEY", os.getenv("DEEPSEEK_API_KEY", ""))
    qwen_base_url: str = os.getenv(
        "QWEN_BASE_URL",
        os.getenv("LLM_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1"),
    )
    model_name: str = os.getenv("MODEL_NAME", "qwen-plus")
    enable_mock_llm: bool = _bool_env("ENABLE_MOCK_LLM", True)
    vector_store_path: str = os.getenv("VECTOR_STORE_PATH", "./data/vector_store.json")


settings = Settings()
