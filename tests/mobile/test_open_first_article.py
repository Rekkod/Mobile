import allure
import pytest
from allure_commons.types import AttachmentType
from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import NoSuchElementException

from utils.locators import POPUP_CLOSE_BUTTON
from utils.onboarding import skip_onboarding_if_present

pytestmark = pytest.mark.mobile


@allure.title("Открытие статьи из подсказок")
def test_open_first_article(mobile_driver):
    driver = mobile_driver

    with allure.step("Пропускаем онбординг, если он есть"):
        skip_onboarding_if_present(driver)

    with allure.step("Открываем поиск и вводим запрос"):
        driver.find_element(AppiumBy.ACCESSIBILITY_ID, "Search Wikipedia").click()
        search = driver.find_element(AppiumBy.ID, "org.wikipedia.alpha:id/search_src_text")
        search.send_keys("Python")

    with allure.step("Выбираем первую подсказку"):
        suggestions = driver.find_elements(AppiumBy.ID, "org.wikipedia.alpha:id/page_list_item_title")
        assert suggestions, "Подсказки не появились"
        suggestions[0].click()

    with allure.step("Закрываем всплывающее окно, если появилось"):
        try:
            driver.find_element(*POPUP_CLOSE_BUTTON).click()
        except NoSuchElementException:
            pass

    with allure.step("Проверяем, что статья открылась"):
        titles = driver.find_elements(AppiumBy.ID, "org.wikipedia.alpha:id/view_page_title_text")
        assert titles, "Заголовок статьи не найден"
        allure.attach(
            titles[0].text if titles else "",
            name="article title",
            attachment_type=AttachmentType.TEXT,
        )
