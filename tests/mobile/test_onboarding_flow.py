import pytest
import allure
from appium.webdriver.common.appiumby import AppiumBy
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

    for name, action_label, locator in screens:
        with allure.step(f"Onboarding: {name} — проверяем контент"):
            title = wait.until(EC.visibility_of_element_located((by, ONBOARDING_TITLE_ID)))
            subtitle = wait.until(EC.visibility_of_element_located((by, ONBOARDING_SUBTITLE_ID)))
            indicator = wait.until(EC.presence_of_element_located((by, ONBOARDING_INDICATOR_ID)))

            assert title.text.strip(), "Заголовок онбординга отсутствует"
            assert subtitle.text.strip(), "Описание онбординга отсутствует"
            indicator_text = indicator.get_attribute("text") or indicator.get_attribute("contentDescription")
            assert indicator_text, "Индикатор прогресса онбординга пустой"

        with allure.step(f"Onboarding: {name} — нажимаем {action_label}"):
            wait.until(EC.element_to_be_clickable(locator)).click()
