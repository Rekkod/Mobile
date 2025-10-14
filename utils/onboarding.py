from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .locators import (
    ONBOARDING_FORWARD_ID, ONBOARDING_DONE_ID, ONBOARDING_SKIP_ID, ONBOARDING_INDICATOR_ID
)

def complete_onboarding(driver, expected_pages: int = 4, timeout: int = 10):
    wait = WebDriverWait(driver, timeout)
    by = AppiumBy.ID
    for i in range(1, expected_pages):
        wait.until(EC.element_to_be_clickable((by, ONBOARDING_FORWARD_ID))).click()
    wait.until(EC.element_to_be_clickable((by, ONBOARDING_DONE_ID))).click()

def skip_onboarding_if_present(driver, timeout: int = 2):
    by = AppiumBy.ID
    try:
        WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((by, ONBOARDING_SKIP_ID))
        ).click()
        return True
    except Exception:
        return False
