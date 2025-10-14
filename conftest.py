import os
import pytest
import allure
import requests
from appium import webdriver
from appium import webdriver
from appium.options.android import UiAutomator2Options
from config import load_config

def _attach_bs_video(session_id: str):
    user = os.getenv('BROWSERSTACK_USERNAME')
    key = os.getenv('BROWSERSTACK_ACCESS_KEY')
    if not (user and key):
        return
    try:
        r = requests.get(
            f'https://api.browserstack.com/app-automate/sessions/{session_id}.json',
            auth=(user, key),
            timeout=20
        )
        video_url = r.json().get('automation_session', {}).get('video_url')
        if video_url:
            html = f'<html><body><video width="100%" controls autoplay><source src="{video_url}" type="video/mp4"></video></body></html>'
            allure.attach(html, name='BrowserStack video', attachment_type=allure.attachment_type.HTML)
    except Exception:
        pass

def pytest_addoption(parser):
    parser.addoption("--env", action="store", default=os.getenv("ENV", "bstack"), help="local | bstack")

@pytest.fixture(scope="session")
def cfg(request):
    env = request.config.getoption("--env")
    return load_config(env)

@pytest.fixture(scope='function')
def mobile_driver(cfg):
    if cfg.env == "bstack":
        caps = {
            "platformName": "android",
            "appium:automationName": "UiAutomator2",
            "app": cfg.app_id,
            "bstack:options": {
                "projectName": "Mobile Wikipedia",
                "buildName": "mobile-wiki",
                "sessionName": "pytest",
                "deviceName": cfg.device,
                "osVersion": cfg.os_version,
                "debug": True,
                "networkLogs": True,
                "video": True,
                "userName": cfg.username,  # ← добавить
                "accessKey": cfg.access_key
            }
        }
        options = UiAutomator2Options().load_capabilities(caps)
        driver = webdriver.Remote("http://hub.browserstack.com/wd/hub", options=options)
    else:
        caps = {
            "platformName": "Android",
            "appium:automationName": "UiAutomator2",
            "appium:appPackage": cfg.app_package,
            "appium:appActivity": cfg.app_activity,
            "appium:noReset": True,
            "appium:newCommandTimeout": 120
        }
        options = UiAutomator2Options().load_capabilities(caps)
        driver = webdriver.Remote(cfg.appium_server, options=options)

    yield driver

    try:
        png = driver.get_screenshot_as_png()
        allure.attach(png, name="last screenshot", attachment_type=allure.attachment_type.PNG)
        src = driver.page_source
        allure.attach(src, name="page source", attachment_type=allure.attachment_type.XML)
        if cfg.env == "bstack":
            _attach_bs_video(driver.session_id)
    finally:
        driver.quit()