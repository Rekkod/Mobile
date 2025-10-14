import json
import os

import allure
import pytest
import requests
from appium import webdriver
from appium.options.android import UiAutomator2Options

from config import load_config


def _attach_bs_video(session_id: str):
    user = os.getenv("BROWSERSTACK_USERNAME")
    key = os.getenv("BROWSERSTACK_ACCESS_KEY")
    if not (user and key):
        return
    try:
        r = requests.get(
            f"https://api.browserstack.com/app-automate/sessions/{session_id}.json",
            auth=(user, key),
            timeout=20,
        )
        video_url = r.json().get("automation_session", {}).get("video_url")
        if video_url:
            html = (
                "<html><body><video width=\"100%\" controls autoplay>"
                f"<source src=\"{video_url}\" type=\"video/mp4\"></video></body></html>"
            )
            allure.attach(html, name="BrowserStack video", attachment_type=allure.attachment_type.HTML)
    except Exception:
        pass


def pytest_addoption(parser):
    parser.addoption("--env", action="store", default=os.getenv("ENV", "bstack"), help="local | bstack")
    parser.addoption(
        "--context",
        action="store",
        default=os.getenv("CONTEXT"),
        help="Имя контекста для загрузки .env.<context>",
    )


@pytest.fixture(scope="session")
def cfg(request):
    env = request.config.getoption("--env")
    context = request.config.getoption("--context")
    config_obj = load_config(env, context=context)
    try:
        allure.dynamic.environment(context=config_obj.context, env=config_obj.env)  # type: ignore[attr-defined]
    except AttributeError:
        # allure.dynamic.environment может отсутствовать при запуске без Allure.
        pass
    return config_obj


@pytest.fixture(scope="function")
def mobile_driver(cfg, request):
    test_name = request.node.name
    capabilities = cfg.capabilities(test_name)
    options = UiAutomator2Options().load_capabilities(capabilities)
    driver = webdriver.Remote(cfg.remote_url(), options=options)

    safe_config = json.dumps(cfg.safe_dump(), ensure_ascii=False, indent=2)
    safe_caps = json.dumps(cfg.sanitize_capabilities(capabilities), ensure_ascii=False, indent=2)
    allure.attach(safe_config, name="runtime config", attachment_type=allure.attachment_type.JSON)
    allure.attach(safe_caps, name="capabilities", attachment_type=allure.attachment_type.JSON)

    if cfg.env == "bstack":
        try:
            driver.execute_script(
                'browserstack_executor: {"action": "setSessionName", "arguments": {"name": "%s"}}' % test_name
            )
        except Exception:
            pass

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
