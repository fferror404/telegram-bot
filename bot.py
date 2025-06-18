
import json
import os
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import logging

API_TOKEN = 'AAHzGVDRjAEKpn_UA6CZsZHvUoH5XFoHwzw'  # ← иваз кунед
CHANNEL_USERNAME = '@Taj_garant'
ADMIN_IDS = [8035955726]

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)

PRODUCTS_FILE = 'products.json'

def load_products():
    if not os.path.exists(PRODUCTS_FILE):
        return {}
    with open(PRODUCTS_FILE, 'r') as f:
        return json.load(f)

def save_products(products):
    with open(PRODUCTS_FILE, 'w') as f:
        json.dump(products, f, indent=2)

products = load_products()

async def check_subscription(user_id):
    member = await bot.get_chat_member(CHANNEL_USERNAME, user_id)
    return member.status in ['member', 'administrator', 'creator']

@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    if not await check_subscription(message.from_user.id):
        kb = InlineKeyboardMarkup().add(
            InlineKeyboardButton("📢 Обуна шудан", url=f"https://t.me/{CHANNEL_USERNAME.strip('@')}"))
        await message.answer("Лутфан аввал ба канали мо обуна шавед:", reply_markup=kb)
        return

    if products:
        for pid, p in products.items():
            btn = InlineKeyboardMarkup().add(
                InlineKeyboardButton("📩 Фиристодан ба админ", callback_data=f"send_{pid}")
            )
            await message.answer_photo(photo=p["photo"], caption=f"📦 {p['title']}\n💰 {p['price']}", reply_markup=btn)
    else:
        await message.answer("Ҳоло маҳсулот нест.")

    search_kb = InlineKeyboardMarkup().add(
        InlineKeyboardButton("🔍 Поиск ID", callback_data="search_id")
    )
    await message.answer("Интихоби дигар:", reply_markup=search_kb)

@dp.callback_query_handler(lambda c: c.data == "search_id")
async def search_id_start(callback: types.CallbackQuery):
    await callback.message.answer("ID-и маҳсулотро ворид кунед:")
    await callback.answer()
    dp.register_message_handler(get_product_by_id, lambda msg: True, state=None)

async def get_product_by_id(message: types.Message):
    pid = message.text.strip()
    if pid in products:
        p = products[pid]
        await message.answer_photo(photo=p["photo"], caption=f"📦 {p['title']}\n💰 {p['price']}")
    else:
        await message.answer("❌ Маҳсулот ёфт нашуд.")
    dp.message_handlers.unregister(get_product_by_id)

@dp.callback_query_handler(lambda c: c.data.startswith("send_"))
async def send_to_admin(callback: types.CallbackQuery):
    pid = callback.data.split("_")[1]
    user = callback.from_user
    if pid in products:
        p = products[pid]
        text = f"📥 Харидор: {user.full_name} (@{user.username})\nИнтихоб кард: {p['title']}\n💰 Нарх: {p['price']}"
        for admin in ADMIN_IDS:
            try:
                await bot.send_message(admin, text)
            except:
                pass
        await callback.message.answer("✅ Маълумот ба админ фиристода шуд.")
    await callback.answer()

@dp.message_handler(commands=['add'])
async def add_product(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        return await message.answer("⛔ Шумо иҷозат надоред.")
    try:
        args = message.text.split("|")
        pid = args[0].split()[1].strip()
        title = args[1].strip()
        price = args[2].strip()
        photo = args[3].strip()
        products[pid] = {"title": title, "price": price, "photo": photo}
        save_products(products)
        await message.answer("✅ Маҳсулот илова шуд.")
    except:
        await message.answer("❌ Формат хатост:\n`/add 1 | Самбӯса | 10 сомонӣ | https://link.jpg`")

@dp.message_handler(commands=['list'])
async def list_products(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    if not products:
        await message.answer("📭 Маҳсулот вуҷуд надорад.")
    else:
        text = "\n".join([f"🆔 {pid}: {p['title']} - {p['price']}" for pid, p in products.items()])
        await message.answer("📋 Рӯйхати маҳсулот:\n\n" + text)

@dp.message_handler(commands=['delete'])
async def delete_product(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    try:
        pid = message.text.split()[1]
        if pid in products:
            del products[pid]
            save_products(products)
            await message.answer(f"🗑 Маҳсулот бо ID {pid} ҳазф шуд.")
        else:
            await message.answer("❌ Маҳсулот ёфт нашуд.")
    except:
        await message.answer("❌ Истифода: /delete ID")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
