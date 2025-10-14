import os
import pytest
from dotenv import load_dotenv
from appium import webdriver
from appium.options.android import UiAutomator2Options
from utils.attach import add_screenshot, add_html, add_logs, add_video

load_dotenv()

@pytest.fixture(scope="session")
def credentials():
    username = os.getenv("BROWSERSTACK_USERNAME")
    access_key = os.getenv("BROWSERSTACK_ACCESS_KEY")
    assert username and access_key, "BROWSERSTACK_USERNAME/BROWSERSTACK_ACCESS_KEY не заданы"
    return username, access_key

@pytest.fixture(scope="session")
def capabilities():
    opts = UiAutomator2Options().load_capabilities({
        "platformName": "android",
        "platformVersion": "12.0",
        "deviceName": "Samsung Galaxy S22 Ultra",
        "app": os.getenv("BS_APP_ID", "bs://e7b6da8bd2027a9048fd07582a40076782c9a62e"),
    })
    return opts

@pytest.fixture(scope="function")
def driver(credentials, capabilities, request):
    username, access_key = credentials
    drv = webdriver.Remote(
        f"http://{username}:{access_key}@hub.browserstack.com/wd/hub",
        options=capabilities
    )
    yield drv

    try:
        add_screenshot(drv)
        add_html(drv)
        add_logs(drv)
        add_video(drv.session_id)
    finally:
        drv.quit()