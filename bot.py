import logging
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import MessageHandler, filters

from dotenv import load_dotenv
import os

load_dotenv('/home/pi/.env')

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = int(os.getenv("TELEGRAM_CHAT_ID"))
ESP32_IP = os.getenv("ESP32_IP")

logging.basicConfig(level=logging.INFO)

async def foto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != CHAT_ID:
        await update.message.reply_text("No autorizado.")
        return
    await update.message.reply_text("Sacando foto...")
    try:
        response = requests.get(f"http://{ESP32_IP}/capture", timeout=10)
        await context.bot.send_photo(
            chat_id=CHAT_ID,
            photo=response.content
        )
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != CHAT_ID:
        return
    if update.message.text == "🚗 Comprobar parking":
        await foto(update, context)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["🚗 Comprobar parking"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "¡Hola! Pulsa el botón para sacar una foto.",
        reply_markup=reply_markup
    )

app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("foto", foto))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))


print("Bot iniciado...")
app.run_polling()