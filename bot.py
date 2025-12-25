import os
import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import random
import requests

logging.basicConfig(level=logging.INFO)
BOT_TOKEN = "7728313617:AAHcdvdnKBoLtsfk9mFKK8BLxaknFFygIBw"

def send_sms(phone, message):
    try:
        url = "https://api.netgsm.com.tr/sms/send/get"
        params = {"usercode": "5325943465", "password": "A9B85", "gsmno": phone, "message": message, "msgheader": "LEYLEKTAKSI"}
        requests.get(url, params=params, timeout=10)
    except:
        pass

verification_codes = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[KeyboardButton("📱 Telefon Numaramı Paylaş", request_contact=True)]]
    await update.message.reply_text("🚕 *LEYLEK TAKSİ*\n\nGiriş için telefon numaranızı paylaşın:", parse_mode='Markdown', reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone = update.message.contact.phone_number.replace('+', '').replace(' ', '')
    if phone.startswith('90'): phone = '0' + phone[2:]
    code = str(random.randint(1000, 9999))
    verification_codes[update.effective_user.id] = {'code': code, 'phone': phone}
    send_sms(phone.replace('0', '90', 1), f"Leylek Taksi kodunuz: {code}")
    await update.message.reply_text(f"📱 *{phone}* numarasına kod gönderildi.\n\nKodu yazın:", parse_mode='Markdown', reply_markup=ReplyKeyboardRemove())

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_user.id
    text = update.message.text.strip()
    if chat_id in verification_codes:
        if text == verification_codes[chat_id]['code']:
            del verification_codes[chat_id]
            keyboard = [[KeyboardButton("🟢 AKTİF"), KeyboardButton("🔴 MEŞGUL")]]
            await update.message.reply_text("✅ *GİRİŞ BAŞARILI!*", parse_mode='Markdown', reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
        else:
            await update.message.reply_text("❌ Hatalı kod!")
        return
    if "AKTİF" in text: await update.message.reply_text("🟢 *AKTİF* - Konum gönderin", parse_mode='Markdown')
    elif "MEŞGUL" in text: await update.message.reply_text("🔴 *MEŞGUL*", parse_mode='Markdown')

async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📍 Konum alındı! İş bekliyorsunuz...")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.CONTACT, handle_contact))
    app.add_handler(MessageHandler(filters.LOCATION, handle_location))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
