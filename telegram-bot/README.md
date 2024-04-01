# Описание

Здесь находится код телеграмм-бота, который используется для взаимодействия с
большими языковыми моделями, доступными через интерфейс **Ollama**. В нем есть
возможность переключаться между доступными на серверной части моделями.

Бот доступен по адресу: https://t.me/mac_adviser_bot

# Запуск без Docker

## 1. Установить ollama

### Linux
``
curl -fsSL https://ollama.com/install.sh | sh
``

### MacOS

``
https://ollama.com/download/mac
``

### Windows
``
https://ollama.com/download/windows
``

Необходимо также загрузить языковую модель, которая будет применяться.

## 2. Настроить переменные в файле .env

* ``TOKEN`` - Токен телеграмм-бота
* ``MODEL`` - используемая изначальная языковая модель (название для API ollama)
* ``OLLAMA_BASE_URL`` - URL для запроса к ollama
* ``OLLAMA_PORT`` - порт, через который следует подключаться к ollama
* ``LOG_LEVEL`` - тип логгирования

## 3. Запустить виртуальное окружение и установить зависимости

С использованием pip (пока что без других пакетных менеджеров Python, таких как
Poetry, Rye и т.д.).

```
pip install -r requirements.txt
```

## 4. Запустить телеграмм-бота

```
python bot.py
```

# Запуск через Docker

```
coming soon...
```