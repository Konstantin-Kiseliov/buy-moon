from aiogram import Bot, Dispatcher, executor, types

from aiogram.contrib.fsm_storage.memory import (
    MemoryStorage,
)  # импорт класса хранения локальных данных, введённых пользователем
from aiogram.dispatcher.filters.state import (
    StatesGroup,
    State,
)  # импорт объектов состояний
from aiogram.dispatcher import (
    FSMContext,
)  # импорт класса, отвечающего за машинное состояние

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import re  # импорт модуля регулярных выражений

from config import TOKEN_API

storage = (
    MemoryStorage()
)  # создание хранилища (экземпляра класса MemoryStorage) локальных данных, введённых пользователем
bot = Bot(TOKEN_API)
dp = Dispatcher(bot=bot, storage=storage)


class ProfileStatesGroup(StatesGroup):
    nickname = State()
    date_of_birth = State()


START_MESSAGE = "Здравствуйте"


def get_start_ikb() -> InlineKeyboardMarkup:
    start_ikb = InlineKeyboardMarkup(row_width=2)
    start_b1 = InlineKeyboardButton(text="Да", callback_data="Yes_registration")
    start_b2 = InlineKeyboardButton(text="Нет", callback_data="No_registration")
    start_ikb.add(start_b1, start_b2)
    return start_ikb


def get_main_kb() -> ReplyKeyboardMarkup:
    main_kb = ReplyKeyboardMarkup(
        resize_keyboard=True
    )  # аргумент в скобках отвечает за то, чтобы клавиатура красиво встраивалась в интерфейс
    main_b1 = KeyboardButton(text="Купить участок")
    main_b2 = KeyboardButton(text="Продать участок")
    main_b3 = KeyboardButton(text="Заработать деньги")
    main_b4 = KeyboardButton(text="Открыть профиль")
    main_kb.add(main_b1, main_b2).add(main_b3, main_b4)
    return main_kb


async def on_startup(_):
    print("Бот был успешно запущен!")


@dp.message_handler(commands=["start"])
async def send_start_message(message: types.Message) -> None:
    await message.answer(START_MESSAGE, parse_mode="HTML", reply_markup=get_start_ikb())


@dp.callback_query_handler()
async def callback_registration(callback: types.CallbackQuery) -> None:
    if callback.data == "Yes_registration":
        await callback.message.answer(
            text="Вы просто космос! Придумайте и отправьте в чат ваш игровой никнейм.\
                                            Никнейм обязательно должен содержать только буквы латинского алфавита и цифры.\
                                            Ограничение по длине: 25 символов."
        )
        await ProfileStatesGroup.nickname.set()
    if callback.data == "No_registration":
        await callback.message.answer(
            text="Сэр, да вы шутник. Но давайте уже как-то посерьёзнее. Пройти регистрацию?",
            reply_markup=get_start_ikb(),
        )


@dp.message_handler(
    lambda message: not message.text.isalnum() or len(message.text) >= 25,
    state=ProfileStatesGroup.nickname,
)
async def check_nickname(message: types.Message):
    await message.reply(
        text="Некорректный никнейм. Придумайте другой и отправьте в чат."
    )


@dp.message_handler(state=ProfileStatesGroup.nickname)
async def load_nickname(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        data["nickname"] = message.text
        await message.reply(
            text=f"Прекрасный никнейм! Оригинальность ваше второе имя, мистер {message.text}.\
                                   Теперь напишите вашу дату рождения цифрами через слэш(или обратный слэш или точку или дефис)."
        )
        await ProfileStatesGroup.next()


@dp.message_handler(
    lambda message: not re.match(
        r"^(?:0[1-9]|[12]\d|3[01])([\/.-])(?:0[1-9]|1[012])\1(?:19|20)\d\d$",
        message.text,
    ),
    state=ProfileStatesGroup.date_of_birth,
)
async def check_date_of_birth(message: types.Message):
    await message.reply(
        text="Некорректная дата. Напишите дату рождения правильно и по рекомендации."
    )


@dp.message_handler(state=ProfileStatesGroup.date_of_birth)
async def load_date_of_birth(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        data["date_of_birth"] = message.text
        print(data)

    await state.finish()
    await message.reply(
        text=f"Регистрация прошла успешно! Вы находитесь в главном меню.",
        reply_markup=get_main_kb(),
    )


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
