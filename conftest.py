import json
import os
from contextlib import suppress

import allure
import pytest
import requests
from allure_commons.types import AttachmentType
from appium import webdriver

from config import load_config


def _attach_bs_video(session_id: str) -> None:
    user = os.getenv("BROWSERSTACK_USERNAME")
    key = os.getenv("BROWSERSTACK_ACCESS_KEY")
    if not (user and key):
        return
    try:
        response = requests.get(
            f"https://api.browserstack.com/app-automate/sessions/{session_id}.json",
            auth=(user, key),
            timeout=20,
        )
        response.raise_for_status()
        video_url = response.json().get("automation_session", {}).get("video_url")
        if video_url:
            html = (
                "<html><body><video width=\"100%\" controls autoplay>"
                f"<source src=\"{video_url}\" type=\"video/mp4\"></video></body></html>"
            )
            allure.attach(html, name="BrowserStack video", attachment_type=AttachmentType.HTML)
    except Exception:
        pass


def _set_bs_status(driver, status: str, reason: str) -> None:
    payload = json.dumps(
        {
            "action": "setSessionStatus",
            "arguments": {
                "status": status,
                "reason": reason[:255],
            },
        }
    )
    driver.execute_script(f"browserstack_executor: {payload}")


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption("--env", action="store", default=os.getenv("ENV", "bstack"), help="local | bstack")
    parser.addoption(
        "--context",
        action="store",
        default=os.getenv("CONTEXT"),
        help="Имя контекста для загрузки .env.<context>",
    )


@pytest.fixture(scope="session")
def cfg(request: pytest.FixtureRequest):
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
    test_name = getattr(getattr(request.node, "callspec", None), "id", request.node.name)
    capabilities = cfg.capabilities(test_name)
    options = cfg.build_options(test_name)
    driver = webdriver.Remote(cfg.remote_url(), options=options)

    safe_config = json.dumps(cfg.safe_dump(), ensure_ascii=False, indent=2)
    safe_caps = json.dumps(cfg.sanitize_capabilities(capabilities), ensure_ascii=False, indent=2)
    allure.attach(safe_config, name="runtime config", attachment_type=AttachmentType.JSON)
    allure.attach(safe_caps, name="capabilities", attachment_type=AttachmentType.JSON)

    if cfg.env == "bstack":
        with suppress(Exception):
            payload = json.dumps(
                {
                    "action": "setSessionName",
                    "arguments": {"name": test_name},
                }
            )
            driver.execute_script(f"browserstack_executor: {payload}")

    request.node._is_bstack = cfg.env == "bstack"  # type: ignore[attr-defined]
    request.node._mobile_driver = driver  # type: ignore[attr-defined]
    request.node._session_name = test_name  # type: ignore[attr-defined]

    yield driver

    try:
        png = driver.get_screenshot_as_png()
        allure.attach(png, name="last screenshot", attachment_type=AttachmentType.PNG)
        src = driver.page_source
        allure.attach(src, name="page source", attachment_type=AttachmentType.XML)
        if cfg.env == "bstack":
            _attach_bs_video(driver.session_id)
    finally:
        driver.quit()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    if rep.when != "call":
        return

    driver = getattr(item, "_mobile_driver", None)
    is_bstack = getattr(item, "_is_bstack", False)
    if not driver or not is_bstack:
        return

    if rep.passed:
        status = "passed"
        reason = "Тест успешно завершен"
    elif rep.skipped:
        status = "passed"
        skip_reason = rep.longrepr[2] if isinstance(rep.longrepr, tuple) and len(rep.longrepr) == 3 else "Тест пропущен"
        reason = skip_reason
    else:
        status = "failed"
        reason = rep.longreprtext.splitlines()[-1] if rep.longrepr else "Тест завершен с ошибкой"

    with suppress(Exception):
        _set_bs_status(driver, status, reason)
