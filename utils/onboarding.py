from appium.webdriver.common.appiumby import AppiumBy
from appium.webdriver.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from .locators import (
    ONBOARDING_DONE_ID,
    ONBOARDING_FORWARD_ID,
    ONBOARDING_SKIP_ID,
)


def complete_onboarding(driver: WebDriver, expected_pages: int = 4, timeout: int = 10) -> None:
    """Пошагово пройти онбординг."""

    wait = WebDriverWait(driver, timeout)
    by = AppiumBy.ID
    for _ in range(1, expected_pages):
        wait.until(EC.element_to_be_clickable((by, ONBOARDING_FORWARD_ID))).click()
    wait.until(EC.element_to_be_clickable((by, ONBOARDING_DONE_ID))).click()


def skip_onboarding_if_present(driver: WebDriver, timeout: int = 2) -> bool:
    """Попытаться пропустить онбординг, если кнопка "Skip" доступна."""

    by = AppiumBy.ID
    try:
        WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((by, ONBOARDING_SKIP_ID))
        ).click()
        return True
    except Exception:
        return False
