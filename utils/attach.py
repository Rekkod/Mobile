import os
import allure
from allure_commons.types import AttachmentType

def add_screenshot(_browser):
    try:
        allure.attach(
            _browser.get_screenshot_as_png(),
            name='screenshot',
            attachment_type=AttachmentType.PNG,
        )
    except Exception:
        pass

def add_html(_browser):
    try:
        allure.attach(
            _browser.page_source,
            name='page_source',
            attachment_type=AttachmentType.HTML,
        )
    except Exception:
        pass

def add_logs(_browser):
    try:
        logs = '\n'.join([str(line) for line in _browser.get_log('logcat')])
        allure.attach(logs, name='device_logs', attachment_type=AttachmentType.TEXT)
    except Exception:
        pass

def add_video(session_id):
    try:
        host = os.getenv('BROWSERSTACK_VIDEO_HOST', 'app-automate.browserstack.com')
        url = f'https://{host}/builds.json'  # резерв
        url = f'https://{host}/sessions/{session_id}.json'
        allure.attach(url, name='video_url', attachment_type=AttachmentType.URI_LIST)
    except Exception:
        pass