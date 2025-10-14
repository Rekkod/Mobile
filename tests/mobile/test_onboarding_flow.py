import json

import pytest
import allure
from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from utils.locators import (
    ONBOARDING_FORWARD_ID,
    ONBOARDING_DONE_ID,
    ONBOARDING_INDICATOR_ID,
    ONBOARDING_TITLE_ID,
    ONBOARDING_SUBTITLE_ID,
)

pytestmark = pytest.mark.mobile

@allure.title("Проход через онбординг (если он есть)")
def test_onboarding_flow(mobile_driver):
    driver = mobile_driver
    by = AppiumBy.ID
    wait = WebDriverWait(driver, 10)
    try:
        driver.execute_script('browserstack_executor: {"action": "setSessionName", "arguments": {"name":"test_onboarding_flow"}}')
    except Exception:
        pass
    screens = [
        ("экран 1", "Continue", (by, ONBOARDING_FORWARD_ID)),
        ("экран 2", "Continue", (by, ONBOARDING_FORWARD_ID)),
        ("экран 3", "Continue", (by, ONBOARDING_FORWARD_ID)),
        ("финал", "Done", (by, ONBOARDING_DONE_ID)),
    ]
    total_steps = len(screens)

    try:
        wait.until(EC.visibility_of_element_located((by, ONBOARDING_TITLE_ID)))
    except TimeoutException:
        pytest.skip("Онбординг не отображается в текущей сборке")

    for index, (name, action_label, locator) in enumerate(screens, start=1):
        with allure.step(f"Onboarding: {name} — проверяем контент"):
            title = wait.until(EC.visibility_of_element_located((by, ONBOARDING_TITLE_ID)))
            subtitle = wait.until(EC.visibility_of_element_located((by, ONBOARDING_SUBTITLE_ID)))
            indicator = wait.until(EC.presence_of_element_located((by, ONBOARDING_INDICATOR_ID)))

            assert title.text.strip(), "Заголовок онбординга отсутствует"
            assert subtitle.text.strip(), "Описание онбординга отсутствует"
            indicator_text = indicator.get_attribute("text") or indicator.get_attribute("contentDescription") or ""
            assert indicator_text.strip(), "Индикатор прогресса онбординга пустой"
            with allure.step("Фиксируем тексты экрана"):
                payload = {
                    "step": index,
                    "title": title.text.strip(),
                    "subtitle": subtitle.text.strip(),
                    "indicator": indicator_text.strip(),
                }
                allure.attach(
                    json.dumps(payload, ensure_ascii=False, indent=2),
                    name=f"onboarding screen {index}",
                    attachment_type=allure.attachment_type.JSON,
                )
            assert str(index) in indicator_text, "Индикатор не содержит текущий номер шага"
            assert str(total_steps) in indicator_text, "Индикатор не содержит общее число шагов"

        with allure.step(f"Onboarding: {name} — нажимаем {action_label}"):
            wait.until(EC.element_to_be_clickable(locator)).click()
