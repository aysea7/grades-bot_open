import logging
import os
import json

from aiogram import Bot
from aiogram import Dispatcher
from aiogram import types
from aiogram import executor
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

import eqx as e
import spreadsheets as s

TOKEN = "token here"
PROXY_URL = "http://proxy.server:3128"
bot = Bot(token=TOKEN, proxy=PROXY_URL)
logging.basicConfig(level=logging.INFO)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
file = open('lists.json', encoding='utf-8')
string = file.read()
students = dict(json.loads(string)['students'][0])
students_id = dict(json.loads(string)['students_id'][0])
students_id_list = list(json.loads(string)['students_id_list'])
subjects_eqx = dict(json.loads(string)['subjects_eqx'][0])
links_list = dict(json.loads(string)['links_list'][0])
subjects_sheets = dict(json.loads(string)['subjects_sheets'][0])
topics = dict(json.loads(string)['topics'][0])


class UserInput(StatesGroup):
    input = State()
    request = State()


# handler for the grade book view requests
@dp.message_handler(commands="eqx")
async def eqx(message: types.Message, state: FSMContext):
    if int(message.from_user.id) in students_id_list:
        async with state.proxy() as data:
            data['request'] = message.text
        user_id = message.from_user.id
        captcha = await e.get_captcha(user_id)
        await bot.send_photo(user_id, open(captcha, mode="rb"))
        await message.answer('Введи код:')
        await UserInput.input.set()
        os.remove(captcha)


# catches the captcha user response
@dp.message_handler(state=[UserInput.input])
async def process_captcha(message: types.Message, state: FSMContext):
    if int(message.from_user.id) in students_id_list:
        async with state.proxy() as data:
            data['input'] = message.text
            request = data['request']
        await state.finish()
        captcha = str(data['input'])
        user_id = message.from_user.id
        parameters = str(request[5:]).split(' ')
        try:
            name = parameters[0]
            subject = parameters[1]
        except IndexError:
            return await message.answer("Вкажи усі дані:\n\nПрізвище(або all), назва предмета")
        await e.process_captcha(user_id, subject, captcha)
        grades = await e.get_grades(user_id, name)
        await message.answer(grades, parse_mode="HTML")


# adds a grade into the pre-specified Google Sheet
@dp.message_handler(commands="add")
async def add(message: types.Message):
    if int(message.from_user.id) in students_id_list:
        parameters = str(message.text[5:]).split(' ')

        try:
            name = parameters[0]
            subject = parameters[1]
            topic = parameters[2]
            grade = parameters[3]
        except IndexError:
            return await message.answer("Помилка! Перевір дані та спробуй знову.")

        try:
            messagetext = await s.add(subject, name, topic, grade)
            await message.answer(messagetext)
        except:
            await message.answer("Помилка! Перевір дані та спробуй знову.")


# looks up the grades from the pre-specified Google Sheet
@dp.message_handler(commands="look")
async def look(message: types.Message):
    if int(message.from_user.id) in students_id_list:
        parameters = str(message.text[6:]).split(' ')

        try:
            subject = parameters[0]
            topic = parameters[1]
        except IndexError:
            return await message.answer("Помилка! Перевір дані та спробуй знову.")

        try:
            grades = await s.look(subject, topic)
            await message.answer(grades, parse_mode="HTML")
        except:
            await message.answer("Помилка! Перевір дані та спробуй знову.")


# sends a list of Zoom links for classes in different subject
@dp.message_handler(commands="links")
async def links(message: types.Message):
    if int(message.from_user.id) in students_id_list:
        link_kb = InlineKeyboardMarkup()
        for subject, link in zip(links_list.keys(), links_list.values()):
            link_kb.row(InlineKeyboardButton(text=f'{subject}', url=f"{link}"))

        await message.answer(text="Вибери посилання:\n(з фарми скидає щоразу нове)", reply_markup=link_kb)


# when user sends a book and specifies the subject, the file gets saved into a corresponding folder in /documents
@dp.message_handler(commands="addbook")
async def add_book(message: types.Message):
    if int(message.from_user.id) in students_id_list:
        try:
            if message.reply_to_message.document is not None:
                subject_raw = message.text.split(" ")[1]
                subject = ""
                for keys, values in subjects_sheets.items():
                    if str(subject_raw).lower() in values:
                        subject = keys
                    else:
                        pass
                if subject == "":
                    return await message.answer("Такого предмета не існує.")
                file = str(await message.reply_to_message.document.download(destination_dir=f"./documents/{subject}"))
                file_name = file.split(f"./documents/{subject}")[1][:-2][11:]
                try:
                    ext = file_name.split('.')[1]
                    name = message.text.split(" ")[2]
                    os.rename(f"./documents/{subject}/documents/{file_name}", f"./documents/{subject}/{name}.{ext}")
                except IndexError:
                    doc_name = message.reply_to_message.document.file_name
                    os.rename(f"./documents/{subject}/documents/{file_name}", f"./documents/{subject}/{doc_name}")
                await message.answer("Книгу додано. Дякуємо за ваш внесок у майбутнє медицини!")
            else:
                await message.answer("Потрібно відповісти командою на документ.")
        except AttributeError:
            pass


# sends a list of books for a specific subject
@dp.message_handler(commands="book")
async def book(message: types.Message):
    if int(message.from_user.id) in students_id_list:
        subject_raw = message.text.split(" ")[1]
        subject = ""
        for keys, values in subjects_sheets.items():
            if str(subject_raw).lower() in values:
                subject = keys
            else:
                pass
        if subject == "":
            return await message.answer("Такого предмета не існує.")

        chat_id = message.chat.id
        for file in os.listdir(f"./documents/{subject}"):
            if file != "documents":
                await bot.send_document(chat_id, open(f"./documents/{subject}/{file}", "rb"))
        await message.answer("-- -- --")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)