import pytest, allure
from appium.webdriver.common.appiumby import AppiumBy
from utils.onboarding import skip_onboarding_if_present

pytestmark = pytest.mark.mobile

@allure.title("Поиск — показываются подсказки")
def test_wiki_search_suggest(mobile_driver):
    driver = mobile_driver
    try:
        driver.execute_script('browserstack_executor: {"action": "setSessionName", "arguments": {"name": \"test_wiki_search_suggest"}}')
    except Exception:
        pass
    skip_onboarding_if_present(driver)
    d = mobile_driver
    with allure.step("Открываем поиск"):
        d.find_element(AppiumBy.ACCESSIBILITY_ID, "Search Wikipedia").click()
    with allure.step("Вводим запрос и ждём подсказки"):
        search = d.find_element(AppiumBy.ID, "org.wikipedia.alpha:id/search_src_text")
        search.send_keys("Selenium")
        items = d.find_elements(AppiumBy.ID, "org.wikipedia.alpha:id/page_list_item_title")
        assert len(items) > 0
