from pydantic import BaseModel
from typing import Literal
import os
from dotenv import load_dotenv
load_dotenv()

EnvName = Literal["local", "bstack"]

class BaseConfig(BaseModel):
    env: EnvName

class LocalConfig(BaseConfig):
    env: EnvName = "local"
    appium_server: str = os.getenv("APPIUM_SERVER", "http://127.0.0.1:4723/wd/hub")
    platform_version: str = os.getenv("ANDROID_PLATFORM_VERSION", "13")
    device_name: str = os.getenv("ANDROID_DEVICE_NAME", "Android Emulator")
    app_package: str = os.getenv("ANDROID_APP_PACKAGE", "org.wikipedia.alpha")
    app_activity: str = os.getenv("ANDROID_APP_ACTIVITY", "org.wikipedia.main.MainActivity")

class BStackConfig(BaseConfig):
    env: EnvName = "bstack"
    username: str = os.getenv("BROWSERSTACK_USERNAME", "")
    access_key: str = os.getenv("BROWSERSTACK_ACCESS_KEY", "")
    app_id: str = os.getenv("BROWSERSTACK_APP_ID", "")
    device: str = os.getenv("BS_DEVICE", "Google Pixel 7")
    os_version: str = os.getenv("BS_OS_VERSION", "13.0")

def load_config(env: EnvName):
    dotenv_file = ".env"
    load_dotenv(dotenv_file, override=True)
    return LocalConfig() if env == "local" else BStackConfig()
