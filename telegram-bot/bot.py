from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.filters.command import Command, CommandStart
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from functions import *

import asyncio
import traceback
import io
import base64
bot = Bot(token=token)
dp = Dispatcher()
builder = InlineKeyboardBuilder()
builder.row(
    # types.InlineKeyboardButton(text="ℹ️ Информация", callback_data="info"),
    # types.InlineKeyboardButton(text="⚙️ Выбрать модель", callback_data="modelmanager"),
)

commands = [
    types.BotCommand(command="start", description="Запустить бота"),
    types.BotCommand(command="reset", description="Удалить историю"),
    types.BotCommand(command="history", description="Посмотреть историю сообщений"),
]

# OllamaAPI
ACTIVE_CHATS = {}
ACTIVE_CHATS_LOCK = contextLock()
modelname = os.getenv("MODEL")
modelinfo = os.getenv("GENINFO")
mention = None

async def get_bot_info():
    global mention
    if mention is None:
        get = await bot.get_me()
        mention = (f"@{get.username}")
    return mention


# /start command
@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    start_message = f"Привет, <b>{message.from_user.full_name}</b>!\nИспользуемая модель: <code>{modelname}</code>"
    await message.answer(
        start_message,
        parse_mode=ParseMode.HTML,
        reply_markup=builder.as_markup(),
        disable_web_page_preview=True,
    )


# /reset - удаление истории запросов
@dp.message(Command("reset"))
async def command_reset_handler(message: Message) -> None:
    if message.from_user.id in ACTIVE_CHATS:
        async with ACTIVE_CHATS_LOCK:
            ACTIVE_CHATS.pop(message.from_user.id)
        logging.info(f"Chat has been reset for {message.from_user.first_name}")
        await bot.send_message(
            chat_id=message.chat.id,
            text="История запросов была очищена",
        )


# /history - получение истории запросов
@dp.message(Command("history"))
async def command_get_context_handler(message: Message) -> None:
    if message.from_user.id in ACTIVE_CHATS:
        messages = ACTIVE_CHATS.get(message.chat.id)["messages"]
        context = ""
        for msg in messages:
            context += f"*{msg['role'].capitalize()}*: {msg['content']}\n"
        await bot.send_message(
            chat_id=message.chat.id,
            text=context,
            parse_mode=ParseMode.MARKDOWN,
        )
    else:
        await bot.send_message(
            chat_id=message.chat.id,
            text="История запросов пустая",
        )


@dp.callback_query(lambda query: query.data == "modelmanager")
async def modelmanager_callback_handler(query: types.CallbackQuery):
    models = await model_list()
    modelmanager_builder = InlineKeyboardBuilder()
    for model in models:
        modelname = model["name"]
        modelfamilies = ""
        if model["details"]["families"]:
            modelicon = {"llama": "🦙", "clip": "📷"}
            try:
                modelfamilies = "".join([modelicon[family] for family in model['details']['families']])
            except KeyError as e:
                # Use a default value when the key is not found
                modelfamilies = f"✨"
        # Add a button for each model
        modelmanager_builder.row(
            types.InlineKeyboardButton(
                text=f"{modelname} {modelfamilies}", callback_data=f"model_{modelname}"
            )
        )
    await query.message.edit_text(
        f"Доступно моделей: {len(models)}\n🦙 = Обычная\n🦙📷 = Мультимодальная", reply_markup=modelmanager_builder.as_markup()
    )


@dp.callback_query(lambda query: query.data.startswith("model_"))
async def model_callback_handler(query: types.CallbackQuery):
    global modelname
    global modelfamily
    modelname = query.data.split("model_")[1]
    await query.answer(f"Выбрана модель: {modelname}")


@dp.callback_query(lambda query: query.data == "info")
async def info_callback_handler(query: types.CallbackQuery):
    dotenv_model = os.getenv("MODEL")
    global modelname
    await bot.send_message(
        chat_id=query.message.chat.id,
        text=f"<b>О моделях</b>\nТекущая модель: <code>{modelname}</code>\nИсходная модель: <code>{dotenv_model}</code>",
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )


# Обработка сообщения
@dp.message()
async def handle_message(message: types.Message):
    await get_bot_info()
    if message.chat.type == "private":
        await ollama_request(message)


async def ollama_request(message: types.Message):
    try:
        await bot.send_chat_action(message.chat.id, "typing")
        prompt = message.text or message.caption
        image_base64 = ''
        if message.content_type == 'photo':
            image_buffer = io.BytesIO()
            await bot.download(
                message.photo[-1],
                destination=image_buffer
            )
            image_base64 = base64.b64encode(image_buffer.getvalue()).decode('utf-8')
        full_response = ""
        sent_message = None
        last_sent_text = None

        async with ACTIVE_CHATS_LOCK:
            if int(is_rag):
                rag_chain = (
                    {"context": docsearch.as_retriever(),  "question": RunnablePassthrough()} 
                    | prompt_template
                )
                prompt = str(rag_chain.invoke(prompt))

            # Add prompt to active chats object
            if ACTIVE_CHATS.get(message.from_user.id) is None:
                ACTIVE_CHATS[message.from_user.id] = {
                    "model": modelname,
                    "messages": [{"role": "user", "content": prompt, "images": ([image_base64] if image_base64 else [])}],
                    "stream": True,
                }
            else:
                ACTIVE_CHATS[message.from_user.id]["messages"].append(
                    {"role": "user", "content": prompt, "images": ([image_base64] if image_base64 else [])}
                )
        logging.info(
            f"[Request]: Processing '{prompt}' for {message.from_user.first_name} {message.from_user.last_name}"
        )
        payload = ACTIVE_CHATS.get(message.from_user.id)
        async for response_data in generate(payload, modelname, prompt):
            msg = response_data.get("message")
            if msg is None:
                continue
            chunk = msg.get("content", "")
            full_response += chunk
            full_response_stripped = full_response.strip()

            # avoid Bad Request: message text is empty
            if full_response_stripped == "":
                continue

            if "." in chunk or "\n" in chunk or "!" in chunk or "?" in chunk:
                if sent_message:
                    if last_sent_text != full_response_stripped:
                        await bot.edit_message_text(chat_id=message.chat.id, message_id=sent_message.message_id,
                                                    text=full_response_stripped)
                        last_sent_text = full_response_stripped
                else:
                    sent_message = await bot.send_message(
                        chat_id=message.chat.id,
                        text=full_response_stripped,
                        reply_to_message_id=message.message_id,
                    )
                    last_sent_text = full_response_stripped

            if response_data.get("done"):
                if (full_response_stripped
                    and last_sent_text != full_response_stripped
                    ):
                    if sent_message:
                        await bot.edit_message_text(chat_id=message.chat.id,
                                                    message_id=sent_message.message_id,
                                                    text=full_response_stripped)
                    else:
                        sent_message = await bot.send_message(chat_id=message.chat.id,
                                                              text=full_response_stripped)
                    
                await bot.edit_message_text(
                    chat_id=message.chat.id,
                    message_id=sent_message.message_id,
                    text=md_autofixer(
                        full_response_stripped + f"\n\nModel: `{modelname}`**\n**Generated in {response_data.get('total_duration') / 1e9:.2f}s"
                    ),
                    parse_mode=ParseMode.MARKDOWN_V2,
                )

                async with ACTIVE_CHATS_LOCK:
                    if ACTIVE_CHATS.get(message.from_user.id) is not None:
                        # Add response to active chats object
                        ACTIVE_CHATS[message.from_user.id]["messages"].append(
                            {"role": "assistant", "content": full_response_stripped}
                        )
                        logging.info(
                            f"[Response]: '{full_response_stripped}' for {message.from_user.first_name} {message.from_user.last_name}"
                        )
                    else:
                        await bot.send_message(
                            chat_id=message.chat.id, text="Chat was reset"
                        )

                break
    except Exception as e:
        await bot.send_message(
            chat_id=message.chat.id,
            # text=f"""Error occurred\n```\n{traceback.format_exc()}\n```""",
            text=f"""Возникла ошибка! Попробуйте ещё раз.""",
            parse_mode=ParseMode.MARKDOWN_V2,
        )


async def main():
    

    await bot.set_my_commands(commands)
    await dp.start_polling(bot, skip_update=True)


if __name__ == "__main__":
    asyncio.run(main())
