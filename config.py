import os
from typing import Literal, Optional

from dotenv import load_dotenv
from pydantic import BaseModel, Field

EnvName = Literal["local", "bstack"]


def _load_context_env(context: str) -> None:
    """Load environment variables for the provided context."""

    dotenv_path = f".env.{context}"
    loaded = load_dotenv(dotenv_path, override=True)
    if not loaded:
        raise FileNotFoundError(
            f"Файл с переменными окружения '{dotenv_path}' не найден. "
            "Создайте его либо укажите корректный контекст."
        )


class BaseConfig(BaseModel):
    env: EnvName
    context: str = Field(default_factory=lambda: os.getenv("CONTEXT", "local_emulator"))


class LocalConfig(BaseConfig):
    env: EnvName = "local"
    appium_server: str = Field(default_factory=lambda: os.getenv("APPIUM_SERVER", "http://127.0.0.1:4723/wd/hub"))
    platform_version: str = Field(default_factory=lambda: os.getenv("ANDROID_PLATFORM_VERSION", "13"))
    device_name: str = Field(default_factory=lambda: os.getenv("ANDROID_DEVICE_NAME", "Android Emulator"))
    app_package: str = Field(default_factory=lambda: os.getenv("ANDROID_APP_PACKAGE", "org.wikipedia.alpha"))
    app_activity: str = Field(default_factory=lambda: os.getenv("ANDROID_APP_ACTIVITY", "org.wikipedia.main.MainActivity"))


class BStackConfig(BaseConfig):
    env: EnvName = "bstack"
    username: str = Field(default_factory=lambda: os.getenv("BROWSERSTACK_USERNAME", ""))
    access_key: str = Field(default_factory=lambda: os.getenv("BROWSERSTACK_ACCESS_KEY", ""))
    app_id: str = Field(default_factory=lambda: os.getenv("BROWSERSTACK_APP_ID", ""))
    device: str = Field(default_factory=lambda: os.getenv("BS_DEVICE", "Google Pixel 7"))
    os_version: str = Field(default_factory=lambda: os.getenv("BS_OS_VERSION", "13.0"))


def load_config(env: EnvName, context: Optional[str] = None):
    """Load configuration for the requested environment and context."""

    load_dotenv(override=True)
    ctx = context or os.getenv(f"CONTEXT_{env.upper()}") or os.getenv("CONTEXT")
    if ctx is None:
        ctx = "local_emulator" if env == "local" else "bstack"

    _load_context_env(ctx)

    config_cls = LocalConfig if env == "local" else BStackConfig
    return config_cls(context=ctx)
