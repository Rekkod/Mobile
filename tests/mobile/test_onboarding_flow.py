import pytest
import allure
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.locators import (
    ONBOARDING_FORWARD_ID, ONBOARDING_DONE_ID, ONBOARDING_INDICATOR_ID
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
    with allure.step("Onboarding: экран 1 — Continue"):
        wait.until(EC.element_to_be_clickable((by, ONBOARDING_FORWARD_ID))).click()
    with allure.step("Onboarding: экран 2 — Continue"):
        wait.until(EC.element_to_be_clickable((by, ONBOARDING_FORWARD_ID))).click()
    with allure.step("Onboarding: экран 3 — Continue"):
        wait.until(EC.element_to_be_clickable((by, ONBOARDING_FORWARD_ID))).click()
    with allure.step("Onboarding: финал — Done"):
        wait.until(EC.element_to_be_clickable((by, ONBOARDING_DONE_ID))).click()
