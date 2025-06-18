import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMINS = ['@fferror404']  # Дуюмро баъд илова мекунед

products = {
    "1": {"name": "Маҳсулот 1", "desc": "Тавсифи маҳсулот 1"},
    "2": {"name": "Маҳсулот 2", "desc": "Тавсифи маҳсулот 2"}
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    buttons = [[InlineKeyboardButton(p['name'], callback_data=f"select_{pid}")] for pid, p in products.items()]
    buttons.append([InlineKeyboardButton("🔍 Поиск ID", callback_data="search_by_id")])
    await update.message.reply_text("Маҳсулотҳоро интихоб кунед:", reply_markup=InlineKeyboardMarkup(buttons))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("select_"):
        product_id = data.split("_")[1]
        product = products.get(product_id)
        if product:
            msg = f"🔹 {product['name']}
{product['desc']}"
            await query.edit_message_text(msg)
            for admin in ADMINS:
                await context.bot.send_message(chat_id=admin, text=f"👤 {query.from_user.full_name} интихоб кард:
{msg}")
    elif data == "search_by_id":
        await query.message.reply_text("Айдиро фиристед:")
        context.user_data["awaiting_id"] = True

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("awaiting_id"):
        pid = update.message.text
        product = products.get(pid)
        if product:
            msg = f"🔹 {product['name']}
{product['desc']}"
            await update.message.reply_text(msg)
        else:
            await update.message.reply_text("❌ Маҳсулот бо чунин ID нест.")
        context.user_data["awaiting_id"] = False

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.run_polling()
