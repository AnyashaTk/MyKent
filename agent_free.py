import logging
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import ContentType
import speech_recognition as sr
import json
from db_operations import save_preference, get_preferences, get_last_location, update_last_location
from stt import speech_to_text_ogg
from io import BytesIO

# from app.stt import speech_to_text_ogg

# Включаем логирование
logging.basicConfig(level=logging.INFO)

# Токен бота
config = json.load(open("config.json"))
API_TOKEN = config["telegram_token"]

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Together AI endpoint
# TOGETHER_API_URL = "https://api.together.xyz/v1/chat/completions"
# TOGETHER_API_MODEL = "meta-llama/Llama-3.3-70B-Instruct-Turbo"  # Укажи модель (например, GPT-JT)

from agent_gpt import ChatGPTTool

chat_tool = ChatGPTTool()
# print(id(chat_tool), 'agent free global')


# Функция для общения с Together AI
def chat_with_together(user_message: str):
    # try:
        # print(id(chat_tool), 'Agent_free chat_with_together')
        img, response = chat_tool.process_user_message(user_message)
        return img, response
    # # except Exception as e:
    #     return None, f"Ошибка подключения: {e}"


# Обработка команды /start
@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    location_button = KeyboardButton("Искать кафе", request_location=True)
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(location_button)

    await message.reply("Привет! Я готов помочь тебе. Напиши текст или отправь голосовое сообщение.",
                        reply_markup=keyboard)


@dp.message_handler(content_types=types.ContentType.LOCATION)
async def handle_location(message: types.Message):
    if message.location:
        user_id = message.from_user.id
        latitude = message.location.latitude
        longitude = message.location.longitude

        update_last_location(user_id=user_id, location=f"{latitude},{longitude}")

        img, response = chat_with_together(f"{latitude},{longitude}")
        await message.reply(response)

    else:
        await message.reply("Не удалось получить местоположение, вы можете его прислать отдельно через вложения, "
                            "если используете мобильное устройство")


@dp.message_handler(commands=["profile"])
async def profile_handler(message: types.Message):
    # ВАЖНО что эта функция находится выше чем обработка всех текстовых сообщений, об этом надо помнить
    user_id = message.from_user.id
    preferences = get_preferences(user_id)
    if preferences:
        await message.reply(f"Ваши предпочтения: {preferences}")
    else:
        await message.reply("Я пока ничего не знаю о ваших предпочтениях.")


@dp.message_handler(commands=["location"])
async def profile_handler(message: types.Message):
    # ВАЖНО что эта функция находится выше чем обработка всех текстовых сообщений, об этом надо помнить
    user_id = message.from_user.id
    preferences = get_last_location(user_id)
    if preferences:
        await message.reply(f"Ваша локация: {get_last_location}")
    else:
        await message.reply("Я пока ничего не знаю о том, где вы.")


# Обработка текстовых сообщений
@dp.message_handler(content_types=ContentType.TEXT)
async def handle_text(message: types.Message):
    user_message = message.text

    user_id = message.from_user.id
    # добавленный код, можно было вывести в отдельную функицю дабы не повторялось,
    # но это надо собирать инфу в строки еще, чтобы отдавать, гптшка все равно все поменяет
    keywords = ["нравится", "люблю", "предпочитаю"]
    for keyword in keywords:
        if keyword in user_message.lower():
            preference = user_message.lower().split(keyword, 1)[1].strip()
            save_preference(user_id, preference)
            await message.reply(f"Запомнил о вас:\n {keyword} {preference}")

    location = get_last_location(user_id)
    print('promt = ', user_message)
    img, response = chat_with_together(user_message)
    if img:
        # Конвертируем PIL Image в объект, который можно отправить через aiogram
        img_byte_array = BytesIO()
        img.save(img_byte_array, format="JPEG")
        img_byte_array.seek(0)
        await message.reply_photo(caption=response, photo=img_byte_array)
    else:
        await message.reply(response)


# Обработка голосовых сообщений
@dp.message_handler(content_types=ContentType.VOICE)
async def handle_voice(message: types.Message):
    file = await bot.get_file(message.voice.file_id)
    file_path = "voice_message.ogg"
    await bot.download_file(file.file_path, file_path)

    user_message = speech_to_text_ogg(file_path)
    if user_message==None:
        await message.reply("Так, можете повторить еще раз? Ничего не понял, что вы сказали)))")
        return
    # добавленный код, можно было вывести в отдельную функицю дабы не повторялось,
    # но это надо собирать инфу в строки еще, чтобы отдавать, гптшка все равно все поменяет
    user_id = message.from_user.id
    keywords = ["нравится", "люблю", "предпочитаю"]

    for keyword in keywords:
        if keyword in user_message.lower():
            preference = user_message.lower().split(keyword, 1)[1].strip()
            save_preference(user_id, preference)
            await message.reply(f"Запомнил о вас:\n {keyword} {preference}")
    # тут этот код заканчивается

    else:
        img, response = chat_with_together(user_message)
        if img:
            # Конвертируем PIL Image в объект, который можно отправить через aiogram
            img_byte_array = BytesIO()
            img.save(img_byte_array, format="JPEG")
            img_byte_array.seek(0)
            await message.reply_photo(caption=response, photo=img_byte_array)
        else:
            await message.reply(response)


# Основная функция запуска
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
