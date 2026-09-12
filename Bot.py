import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

# Tokenni Render'dagi Environment Variable'dan o'qiydi (lokalda sinash uchun o'zingiznikini yozib turishingiz ham mumkin)
TOKEN = os.getenv("BOT_TOKEN", "SIZNING_BOT_TOKENINGIZ")

# FAQT SIZNING TELEGRAM ID RAQAMINGIZ (boshqalar kira olmaydi)
# O'z Telegram ID raqamingizni shu yerga yozing (masalan: 123456789)
ADMIN_ID = 123456789  # <--- O'Z ID RAQAMINGIZNI YOZING!

# Vaqtincha xotirada saqlash uchun
user_balances = {}

class FinanceState(StatesGroup):
    waiting_for_income = State()
    waiting_for_expense = State()

dp = Dispatcher()

# Har qanday xabardan oldin foydalanuvchi Admin ekanligini tekshiruvchi funksiya
@dp.message(F.from_user.id != ADMIN_ID)
async def not_authorized(message: types.Message):
    await message.answer("Kechirasiz, bu bot faqat uning egasi uchun mo'ljallangan. Siz undan foydalana olmaysiz! ❌")

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    if user_id not in user_balances:
        user_balances[user_id] = {"kirim": 0, "chiqim": 0}
    
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="Kirim qo'shish"), types.KeyboardButton(text="Chiqim qo'shish")],
            [types.KeyboardButton(text="Hisobotni ko'rish")]
        ],
        resize_keyboard=True
    )
    await message.answer("Assalomu alaykum! Shaxsiy moliyaviy botingiz ishga tushdi. Kerakli tugmani tanlang:", reply_markup=keyboard)

@dp.message(F.text == "Kirim qo'shish")
async def add_income(message: types.Message, state: FSMContext):
    await message.answer("Qancha kirim qildingiz? (Faqat raqam yozing, masalan: 50000)")
    await state.set_state(FinanceState.waiting_for_income)

@dp.message(FinanceState.waiting_for_income)
async def save_income(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Iltimos, faqat raqam kiriting!")
        return
    
    amount = int(message.text)
    user_id = message.from_user.id
    user_balances[user_id]["kirim"] += amount
    
    await message.answer(f"Muvaffaqiyatli qo'shildi! Jami kirim: {user_balances[user_id]['kirim']} so'm")
    await state.clear()

@dp.message(F.text == "Chiqim qo'shish")
async def add_expense(message: types.Message, state: FSMContext):
    await message.answer("Qancha chiqim qildingiz? (Faqat raqam yozing, masalan: 20000)")
    await state.set_state(FinanceState.waiting_for_expense)

@dp.message(FinanceState.waiting_for_expense)
async def save_expense(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Iltimos, faqat raqam kiriting!")
        return
    
    amount = int(message.text)
    user_id = message.from_user.id
    user_balances[user_id]["chiqim"] += amount
    
    await message.answer(f"Muvaffaqiyatli qo'shildi! Jami chiqim: {user_balances[user_id]['chiqim']} so'm")
    await state.clear()

@dp.message(F.text == "Hisobotni ko'rish")
async def show_report(message: types.Message):
    user_id = message.from_user.id
    data = user_balances.get(user_id, {"kirim": 0, "chiqim": 0})
    balance = data["kirim"] - data["chiqim"]
    
    report = (
        f"📊 Sizning moliyaviy hisobotingiz:\n\n"
        f"🟢 Jami kirim: {data['kirim']} so'm\n"
        f"🔴 Jami chiqim: {data['chiqim']} so'm\n"
        f"💰 Qoldiq: {balance} so'm"
    )
    await message.answer(report)

async def main():
    bot = Bot(token=TOKEN)
    await dp.start_polling(bot)

if name == "main":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
