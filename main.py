import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import CommandStart
from mistralai import Mistral

# Функция для чтения конфигурационного файла


def load_api_keys(file_path):
    api_keys = {}
    with open(file_path, 'r') as file:
        for line in file:
            # Разделяем ключ и значение
            key, value = line.strip().split('=', 1)
            # Убираем кавычки, если они есть
            if value.startswith(("'", '"')) and value.endswith(("'", '"')):
                value = value[1:-1]
            api_keys[key] = value
    return api_keys



# Загрузка API ключей
api_keys = load_api_keys('api.txt')

# Инициализация бота
bot = Bot(token=api_keys['TELEGRAM_BOT_TOKEN'])
dp = Dispatcher()


# Функция взаимодействия с MistralAi
async def ask_neural_network(prompt: str) -> str:
    api_key = api_keys['MISTRAL_API_KEY']
    model = "mistral-tiny"
    client = Mistral(api_key=api_key)

    try:
        response = await client.chat.stream_async(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
        )
        result = ""
        async for chunk in response:
            if chunk.data.choices[0].delta.content is not None:
                result += chunk.data.choices[0].delta.content
        return result
    except Exception as e:
        return f"Ошибка при запросе к нейросети: {str(e)}"

# Обработчик команды /start


@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer('Привет! Напиши мне что-нибудь, и я постараюсь ответить с помощью нейросети.')

# Обработчик любого текстового сообщения


@dp.message(F.text)
async def handle_text_message(message: Message):
    prompt = message.text
    await message.answer("Обрабатываю запрос, подождите...")

    # Взаимодействие с нейросетью
    response = await ask_neural_network(prompt)

    # Ответ пользователю
    await message.answer(response)


async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
