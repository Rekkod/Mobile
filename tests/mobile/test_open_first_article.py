import pytest
import allure
from appium.webdriver.common.appiumby import AppiumBy
from utils.onboarding import skip_onboarding_if_present
from utils.locators import POPUP_CLOSE_BUTTON
from selenium.common.exceptions import NoSuchElementException

pytestmark = pytest.mark.mobile

@allure.title("Открытие статьи из подсказок")
def test_open_first_article(mobile_driver):
    driver = mobile_driver
    try:
        driver.execute_script('browserstack_executor: {"action": "setSessionName", "arguments": {"name": \"test_open_first_article"}}')
    except Exception:
        pass
    skip_onboarding_if_present(driver)
    d = mobile_driver
    d.find_element(AppiumBy.ACCESSIBILITY_ID, "Search Wikipedia").click()
    search = d.find_element(AppiumBy.ID, "org.wikipedia.alpha:id/search_src_text")
    search.send_keys("Python")
    items = d.find_elements(AppiumBy.ID, "org.wikipedia.alpha:id/page_list_item_title")
    assert items, "Подсказки не появились"
    items[0].click()
    try:
        driver.find_element(*POPUP_CLOSE_BUTTON).click()
    except NoSuchElementException:
        pass
    title = d.find_elements(AppiumBy.ID, "org.wikipedia.alpha:id/view_page_title_text")
    assert title, "Заголовок статьи не найден"
