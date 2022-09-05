from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext

from bs4 import BeautifulSoup
import logging
import emoji



from config import TOKEN
from logic import create_browser, Medicament, Condition


storage = MemoryStorage()
bot = Bot(TOKEN)
dp = Dispatcher(bot, storage=storage)
logging.basicConfig(level=logging.WARNING)
medicament = Medicament()



@dp.message_handler(commands='start', state='*')
async def start_welcome(message: types.Message):
    await message.reply(emoji.emojize("Введите лекарственный препарат:beating_heart: : "))
    await Condition.waiting_to_find_drugs.set()
    logging.getLogger().info("/start")


@dp.message_handler(state=Condition.waiting_to_find_drugs)
async def get_menu(message: types.Message, state: FSMContext):
    await message.reply(emoji.emojize('Начинаю поиск лекарственного препарата :timer_clock:'))
    response = create_browser(message.text)
    logging.getLogger().error("response False")

    if response:
        logging.getLogger().info("HTML ready")
        await state.update_data(chosen_drug=message.text)
        with open(f"medikoment{message.chat.id}.html", "w", encoding="utf-8") as file:
            file.write(response)

        with open(f"medikoment{message.chat.id}.html", encoding="utf-8") as file:
            src = file.read()

        soup = BeautifulSoup(src, "lxml")
        # medicament.set_soup(soup)

        instructions_for_the_drug = medicament.instructions(soup)
        logging.getLogger().info("instructions ready")

        numeric_instruction = medicament.numeric_instruction(instructions_for_the_drug)

        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        button_1 = types.KeyboardButton(
            text=emoji.emojize("Чтобы перейти в режим поиска лекарства нажмите сюда :medical_symbol:"))
        keyboard.add(button_1)

        await Condition.next()
        logging.getLogger().info("sending instructions")
        await message.reply(
            text=emoji.emojize(
                f':eight-spoked_asterisk:{message.chat.first_name} '
                f'отправьте мне число интересующей вас характеристики:eight-spoked_asterisk:'),
            reply_markup=keyboard)
        await message.reply('\n'.join(numeric_instruction))

    else:
        await message.reply(emoji.emojize(":warning:Проверьте правильность ввода:warning:"))


@dp.message_handler(state=Condition.waiting_to_find_digit)
async def get_property_for_digit(message: types.Message, state: FSMContext):
    logging.getLogger().info("sending property drug")
    if message.text.isdigit():
        await state.update_data(digit=message.text)
        response_text = medicament.get_annotation(int(message.text), message)
        await message.reply(f'----------{response_text}')
    elif message.text == emoji.emojize(
                                    "Чтобы перейти в режим поиска лекарства нажмите сюда :medical_symbol:"):
        await state.set_state(Condition.waiting_to_find_drugs)
        logging.getLogger().info("level search")
        await message.reply(emoji.emojize(
                                    'Режим поиска лекарства включен, введите препарат :backhand_index_pointing_down:'))
    else:
        await message.reply(emoji.emojize(
            ":warning:Проверьте правильность ввода, нужно ввести цифру из меню выше:warning:"))


if __name__ == '__main__':
    executor.start_polling(dp)
