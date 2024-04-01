import logging
import os
import aiohttp
import json
from aiogram import types
from asyncio import Lock
from functools import wraps
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("TOKEN")
ollama_base_url = os.getenv("OLLAMA_BASE_URL")
ollama_port = os.getenv("OLLAMA_PORT")
log_level_str = os.getenv("LOG_LEVEL", "INFO")

# Настройки логгирования
# ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'NOTSET']
log_levels = list(logging._levelToName.values())

if log_level_str not in log_levels:
    log_level = logging.DEBUG
else:
    log_level = logging.getLevelName(log_level_str)

logging.basicConfig(level=log_level)


# Ollama API
async def model_list():
    async with aiohttp.ClientSession() as session:
        url = f"http://{ollama_base_url}:{ollama_port}/api/tags"
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                return data["models"]
            else:
                return []


async def generate(payload: dict, modelname: str, prompt: str):
    async with aiohttp.ClientSession() as session:
        url = f"http://{ollama_base_url}:{ollama_port}/api/chat"

        async with session.post(url, json=payload) as response:
            async for chunk in response.content:
                if chunk:
                    decoded_chunk = chunk.decode()
                    if decoded_chunk.strip():
                        yield json.loads(decoded_chunk)


def md_autofixer(text: str) -> str:
    escape_chars = r"_[]()~>#+-=|{}.!"
    # Использую экранирование для нежелательных спецсимволов
    return "".join("\\" + char if char in escape_chars else char for char in text)


class contextLock:
    lock = Lock()
    async def __aenter__(self):
        await self.lock.acquire()
    async def __aexit__(self, exc_type, exc_value, exc_traceback):
        self.lock.release()
