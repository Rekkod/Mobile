# Mobile Wikipedia (минимум под требования)

## Запуск локально (Appium)
1) `pip install -r requirements.txt`
2) Создай `.env.local` по образцу `.env.local.example`
3) Запусти Appium (`http://127.0.0.1:4723/wd/hub`) и устройство/эмулятор
4) `pytest -m mobile --env local`

## Запуск на BrowserStack
1) Создай `.env.bstack` по образцу `.env.bstack.example`
2) `pytest -m mobile --env bstack`
