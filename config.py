import os
from copy import deepcopy
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Literal, Optional

from appium.options.android import UiAutomator2Options
from dotenv import load_dotenv
from pydantic import BaseModel, ConfigDict, Field

BASE_DIR = Path(__file__).resolve().parent
EnvName = Literal["local", "bstack"]


def _env_file(context: Optional[str]) -> Path:
    suffix = f".{context}" if context else ""
    return BASE_DIR / f".env{suffix}"


def _load_context_env(context: str) -> None:
    """Load environment variables for the provided context."""

    dotenv_path = _env_file(context)
    loaded = load_dotenv(dotenv_path, override=True)
    if not loaded:
        raise FileNotFoundError(
            f"Файл с переменными окружения '{dotenv_path.name}' не найден. "
            "Создайте его либо укажите корректный контекст."
        )


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


class BaseConfig(BaseModel):
    model_config = ConfigDict(frozen=True, extra="ignore")
    env: EnvName
    context: str = Field(default_factory=lambda: os.getenv("CONTEXT", "local_emulator"))

    def remote_url(self) -> str:
        raise NotImplementedError

    def capabilities(self, test_name: str) -> Dict[str, Any]:
        raise NotImplementedError

    def build_options(self, test_name: str) -> UiAutomator2Options:
        return UiAutomator2Options().load_capabilities(self.capabilities(test_name))

    def safe_dump(self) -> Dict[str, Any]:
        return self.model_dump()

    def sanitize_capabilities(self, caps: Dict[str, Any]) -> Dict[str, Any]:
        return deepcopy(caps)


class LocalConfig(BaseConfig):
    env: EnvName = "local"
    appium_server: str = Field(default_factory=lambda: os.getenv("APPIUM_SERVER", "http://127.0.0.1:4723/wd/hub"))
    platform_version: str = Field(default_factory=lambda: os.getenv("ANDROID_PLATFORM_VERSION", "13"))
    device_name: str = Field(default_factory=lambda: os.getenv("ANDROID_DEVICE_NAME", "Android Emulator"))
    app_package: str = Field(default_factory=lambda: os.getenv("ANDROID_APP_PACKAGE", "org.wikipedia.alpha"))
    app_activity: str = Field(default_factory=lambda: os.getenv("ANDROID_APP_ACTIVITY", "org.wikipedia.main.MainActivity"))
    no_reset: bool = Field(default_factory=lambda: _env_bool("APPIUM_NO_RESET", True))
    auto_grant_permissions: bool = Field(default_factory=lambda: _env_bool("APPIUM_AUTO_GRANT_PERMISSIONS", True))
    adb_exec_timeout: int = Field(default_factory=lambda: _env_int("APPIUM_ADB_EXEC_TIMEOUT", 60000))
    new_command_timeout: int = Field(default_factory=lambda: _env_int("APPIUM_NEW_COMMAND_TIMEOUT", 120))

    def remote_url(self) -> str:
        return self.appium_server

    def capabilities(self, test_name: str) -> Dict[str, Any]:
        return {
            "platformName": "Android",
            "appium:automationName": "UiAutomator2",
            "appium:platformVersion": self.platform_version,
            "appium:deviceName": self.device_name,
            "appium:appPackage": self.app_package,
            "appium:appActivity": self.app_activity,
            "appium:noReset": self.no_reset,
            "appium:autoGrantPermissions": self.auto_grant_permissions,
            "appium:adbExecTimeout": self.adb_exec_timeout,
            "appium:newCommandTimeout": self.new_command_timeout,
        }


class BStackConfig(BaseConfig):
    env: EnvName = "bstack"
    username: str = Field(default_factory=lambda: os.getenv("BROWSERSTACK_USERNAME", ""))
    access_key: str = Field(default_factory=lambda: os.getenv("BROWSERSTACK_ACCESS_KEY", ""))
    app_id: str = Field(default_factory=lambda: os.getenv("BROWSERSTACK_APP_ID", ""))
    device: str = Field(default_factory=lambda: os.getenv("BS_DEVICE", "Google Pixel 7"))
    os_version: str = Field(default_factory=lambda: os.getenv("BS_OS_VERSION", "13.0"))
    project_name: str = Field(default_factory=lambda: os.getenv("BS_PROJECT_NAME", "Mobile Wikipedia"))
    build_name: str = Field(default_factory=lambda: os.getenv("BS_BUILD_NAME", "mobile-wiki"))

    def remote_url(self) -> str:
        return os.getenv("BROWSERSTACK_SERVER", "http://hub.browserstack.com/wd/hub")

    def capabilities(self, test_name: str) -> Dict[str, Any]:
        bstack_options = {
            "projectName": self.project_name,
            "buildName": self.build_name,
            "sessionName": test_name,
            "deviceName": self.device,
            "osVersion": self.os_version,
            "debug": True,
            "networkLogs": True,
            "video": True,
        }
        if self.username:
            bstack_options["userName"] = self.username
        if self.access_key:
            bstack_options["accessKey"] = self.access_key

        return {
            "platformName": "android",
            "appium:automationName": "UiAutomator2",
            "app": self.app_id,
            "bstack:options": bstack_options,
            "appium:autoGrantPermissions": True,
        }

    def safe_dump(self) -> Dict[str, Any]:
        data = super().safe_dump()
        if data.get("access_key"):
            data["access_key"] = "***"
        return data

    def sanitize_capabilities(self, caps: Dict[str, Any]) -> Dict[str, Any]:
        safe_caps = super().sanitize_capabilities(caps)
        bstack_options = safe_caps.get("bstack:options", {})
        if "accessKey" in bstack_options:
            bstack_options["accessKey"] = "***"
        return safe_caps


@lru_cache(maxsize=None)
def load_config(env: EnvName, context: Optional[str] = None) -> BaseConfig:
    """Load configuration for the requested environment and context."""

    load_dotenv(_env_file(None), override=True)  # base .env (optional)
    ctx = context or os.getenv(f"CONTEXT_{env.upper()}") or os.getenv("CONTEXT")
    if ctx is None or not ctx.strip():
        ctx = "local_emulator" if env == "local" else "bstack"
    else:
        ctx = ctx.strip()

    _load_context_env(ctx)

    config_cls = LocalConfig if env == "local" else BStackConfig
    return config_cls(context=ctx)
