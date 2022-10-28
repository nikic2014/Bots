from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.utils import executor
from glQiwiApi import QiwiP2PClient
from glQiwiApi.qiwi.clients.p2p.types import Bill
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
import datetime
from aiohttp import ClientConnectionError
import Token

#TODO: написать удаление юзеров из бд, когда закончится их срок подписки

qiwi_p2p_client = QiwiP2PClient(
    secret_p2p=Token.qiwi_token)

BOT_TOKEN = Token.token

bot = Bot(token=BOT_TOKEN, parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
file_out = open('AllVerifiedUsers.txt', 'a', encoding="utf-8")

button_forks = KeyboardButton('Вилки')
button_payment = KeyboardButton('Оплата')
button_feedback = KeyboardButton('Связь с разработчиком')

greet_kb = ReplyKeyboardMarkup(resize_keyboard=True)
greet_kb.add(button_forks)
greet_kb.add(button_payment)
greet_kb.add(button_feedback)

button_football = KeyboardButton('Футбол')
button_tanis = KeyboardButton('Тенис')
button_back = KeyboardButton('Назад')
greet_kb2 = ReplyKeyboardMarkup(resize_keyboard=True)
greet_kb2.add(button_football)
greet_kb2.add(button_tanis)
greet_kb2.add(button_back)


try:
    @dp.message_handler(state="payment", text='Вилки')
    async def process_start_command(message: types.Message):
        if True : # если оплата прошла
            await message.reply("Ваши вилки", reply_markup=greet_kb2)
        else :
            await message.reply("Оплатите счет", reply_markup=greet_kb2)

    @dp.message_handler(text='Вилки')
    async def process_start_command(message: types.Message):
        if True:  # если оплата прошла
            await message.reply("Ваши вилки", reply_markup=greet_kb2)
        else:
            await message.reply("Оплатите счет", reply_markup=greet_kb2)


    @dp.message_handler(state="payment", text='Назад')
    async def process_start_command(message: types.Message):
        await message.reply("Вы в главном меню", reply_markup=greet_kb)
    @dp.message_handler(text='Назад')
    async def process_start_command(message: types.Message):
        await message.reply("Вы в главном меню", reply_markup=greet_kb)

    @dp.message_handler(text='Оплата')
    async def handle_creation_of_payment(message: types.Message, state: FSMContext):
        async with qiwi_p2p_client:
            bill = await qiwi_p2p_client.create_p2p_bill(amount=1)
        await message.answer(text=f"Ok, here's your invoice:\n {bill.pay_url}")
        await state.set_state("payment")
        await state.update_data(bill=bill)
        file_out = open('Users_payment_url.txt', 'a', encoding="utf-8")
        file_out.write(
            "id: {0}\npayment_url: {1}\n".format(message.from_user.id, bill.pay_url))
        file_out.close()
        # TODO: сделать так, что user не записывался 2 раза


    @dp.message_handler(state="payment", text='Оплата')
    async def handle_creation_of_payment(message: types.Message, state: FSMContext):
        user_id = 'id: ' + str(message.from_user.id) + '\n'
        with open('Users_payment_url.txt', 'r', encoding="utf-8") as file_graph:
            all_lines = file_graph.readlines()

        for i, line in enumerate(all_lines):
            if line == user_id:
                link_line = all_lines[i + 1]
                url = link_line.find(' ')
                finish_url = link_line[url + 1:]
                await message.answer(text=f"Ok, here's your invoice:\n {finish_url}")






    @dp.message_handler(text='Связь с разработчиком')
    async def process_start_command(message: types.Message):
        await message.reply("1: @blackdony \n2: @Sad_prod", reply_markup=greet_kb)

    @dp.message_handler(state="payment", text='Связь с разработчиком')
    async def process_start_command(message: types.Message):
        await message.reply("1: @blackdony \n2: @Sad_prod", reply_markup=greet_kb)


    @dp.message_handler(commands=['start'])
    async def alarm(message: types.Message):
        await message.answer(f"Ваш ID: {message.from_user.id}")
        await message.reply("Привет!", reply_markup=greet_kb)


    @dp.callback_query_handler(text='user_id')
    async def user_id_inline_callback(callback_query: types.CallbackQuery):
        print("Это рабоает!!")
        await callback_query.answer(f"Ваш ID: {callback_query.from_user.id}", True)


    @dp.message_handler(state="payment", text="Привет!")
    async def handle_hi_answer(message: types.Message):
        file_out = open('AllVerifiedUsers.txt', 'r', encoding="utf-8")
        all_text = file_out.readlines()
        if "id: " + str(message.from_user.id) + "\n" in all_text:
            await message.answer("Красачиг!!!")
        else:
            await message.answer("ЛЕЕЕ ЖИДКИЙ!!!")
        file_out.close()


    @dp.message_handler(text="Привет!")
    async def handle_hi_answer(message: types.Message):
        file_out = open('AllVerifiedUsers.txt', 'r', encoding="utf-8")
        all_text = file_out.readlines()
        if "id: " + str(message.from_user.id) + "\n" in all_text:
            await message.answer("Красачиг!!!")
        else:
            await message.answer("ЛЕЕЕ ЖИДКИЙ!!!")
        file_out.close()


    @dp.message_handler(state="payment", text="I have paid this invoice")
    async def handle_successful_payment(message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            bill: Bill = data.get("bill")

        if await qiwi_p2p_client.check_if_bill_was_paid(bill):
            await message.answer("You have successfully paid your invoice")
            file_out = open('AllVerifiedUsers.txt', 'a', encoding="utf-8")
            file_out.write(
                "id: {0}\npayment_url: {1}\ndate: {2}".format(message.from_user.id, bill.pay_url, datetime.datetime.now()))
            file_out.close()
            await state.finish()
        else:
            await message.answer("Invoice was not paid")
except ClientConnectionError:
    print("zalupa")


executor.start_polling(dp, skip_updates= 'true')