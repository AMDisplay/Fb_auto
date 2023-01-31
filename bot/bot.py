import logging

from aiogram import Bot, Dispatcher, executor, types


API_TOKEN = "5873293011:AAF5wTCYfL-4W24drzARmSohNFn8ZlWF3tA"
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)


# Хэндлер на команду /test1
@dp.message_handler(commands="test1")
async def cmd_test1(message: types.Message):
    await message.reply("Test 1")


if __name__ == "__main__":
    # Запуск бота
    executor.start_polling(dp, skip_updates=True)