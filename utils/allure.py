import allure

def attach_text(name: str, text: str):
    allure.attach(text, name=name, attachment_type=allure.attachment_type.TEXT)

def attach_html(name: str, html: str):
    allure.attach(html, name=name, attachment_type=allure.attachment_type.HTML)
