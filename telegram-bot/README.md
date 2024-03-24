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
* ``MODEL`` - используемая языковая модель (название для API ollama)
* ``OLLAMA_BASE_URL`` - URL для запроса к ollama
* ``OLLAMA_PORT`` - порт, через который следует подключаться к ollama
* ``LOG_LEVEL`` - тип логгирования

## 3. Запустить виртуальное окружение и установить зависимости

Использование пакетных менеджеров Python 

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