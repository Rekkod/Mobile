import allure
import pytest
from appium.webdriver.common.appiumby import AppiumBy

from utils.onboarding import skip_onboarding_if_present

pytestmark = pytest.mark.mobile


@allure.title("Поиск — показываются подсказки")
def test_wiki_search_suggest(mobile_driver):
    driver = mobile_driver

    with allure.step("Пропускаем онбординг, если он есть"):
        skip_onboarding_if_present(driver)

    with allure.step("Открываем поиск"):
        driver.find_element(AppiumBy.ACCESSIBILITY_ID, "Search Wikipedia").click()

    with allure.step("Вводим запрос и проверяем подсказки"):
        search = driver.find_element(AppiumBy.ID, "org.wikipedia.alpha:id/search_src_text")
        search.send_keys("Selenium")
        items = driver.find_elements(AppiumBy.ID, "org.wikipedia.alpha:id/page_list_item_title")
        assert len(items) > 0, "Подсказки не появились"
