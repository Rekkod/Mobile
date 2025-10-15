# Mobile Wikipedia тесты

Набор UI-тестов для приложения Wikipedia на Android.

## Подготовка окружения

```bash
pip install -r requirements.txt
```

## Конфигурация

- Основные настройки описаны в `config.py` и управляются через pydantic-модели.
- Значения переменных окружения подгружаются из файлов `.env.<context>` с помощью `python-dotenv`.
- Базовый файл `.env` хранит сопоставление окружений (`local`, `bstack`) с контекстами.

В репозитории добавлены шаблоны контекстов:

- `.env.local_emulator`
- `.env.local_real`
- `.env.bstack`

Скопируйте нужный шаблон и отредактируйте значения под себя. Допускается создание собственных контекстов — файл должен называться `.env.<имя_контекста>`.

## Запуск тестов

### Локально (Appium)

```bash
pytest -m mobile --env local --context local_emulator
```

Поддерживаются флаги `APPIUM_NO_RESET`, `APPIUM_AUTO_GRANT_PERMISSIONS`, `APPIUM_ADB_EXEC_TIMEOUT` и `APPIUM_NEW_COMMAND_TIMEOUT` в `.env.<context>`.

### BrowserStack

```bash
pytest -m mobile --env bstack --context bstack
```

Дополнительно можно задать `BS_PROJECT_NAME` и `BS_BUILD_NAME` через `.env.bstack`. Статус каждой сессии автоматически синхронизируется с BrowserStack (pass/fail/skip).

### Быстрая смена контекста

Контекст можно указать через переменную окружения:

```bash
CONTEXT=local_real pytest -m mobile --env local
```

Или настроить разные контексты для локального и удалённого прогона в `.env`:

```
CONTEXT_LOCAL=local_emulator
CONTEXT_BSTACK=bstack
```

Во время прогона в Allure автоматически подтягиваются данные о выбранном окружении, конфигурации и капабилити.
