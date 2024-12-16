import os
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Environment variables
TELEGRAM_BOT_TOKEN = os.getenv("7778310816:AAHkhL5Q1Kv1qNM4UVKdyKIcUDoB3BXtc_c")
IMGBB_API_KEY = os.getenv("741ef2b341b26c4341f929c2356e4e88")
OWNER_ID = int(os.getenv("5827289728"))  # Your Telegram ID as an integer

# Authorized users list
authorized_users = set()


def start(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if user_id not in authorized_users:
        update.message.reply_text("Access Denied! DM @Soutick_09 to use this Bot.")
    else:
        keyboard = [[InlineKeyboardButton("Developer", url="https://t.me/Soutick_09")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text("Made With ♥️ By Soutick", reply_markup=reply_markup)


def authorise(update: Update, context: CallbackContext):
    if update.effective_user.id != OWNER_ID:
        update.message.reply_text("Only the bot owner can use this command.")
        return

    if len(context.args) != 1:
        update.message.reply_text("Usage: /authorise <user_id_or_username>")
        return

    target = context.args[0]
    try:
        user_id = int(target)
    except ValueError:
        user_id = context.bot.get_chat(target).id

    authorized_users.add(user_id)
    context.bot.send_message(chat_id=user_id, text="Congratulations 🎉! You are now authorized.")
    update.message.reply_text(f"User {target} has been authorized.")


def unauthorise(update: Update, context: CallbackContext):
    if update.effective_user.id != OWNER_ID:
        update.message.reply_text("Only the bot owner can use this command.")
        return

    if len(context.args) != 1:
        update.message.reply_text("Usage: /unauthorise <user_id_or_username>")
        return

    target = context.args[0]
    try:
        user_id = int(target)
    except ValueError:
        user_id = context.bot.get_chat(target).id

    if user_id in authorized_users:
        authorized_users.remove(user_id)
        context.bot.send_message(chat_id=user_id, text="Alas 😭! You have been unauthorized.")
        update.message.reply_text(f"User {target} has been unauthorized.")
    else:
        update.message.reply_text(f"User {target} was not authorized.")


def handle_media(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if user_id not in authorized_users:
        update.message.reply_text("Access Denied! DM @Soutick_09 to use this Bot.")
        return

    file = update.message.photo[-1] if update.message.photo else update.message.document
    file_path = context.bot.get_file(file.file_id).file_path

    # Log "Uploading..."
    status_message = update.message.reply_text("Uploading...")

    # Upload to ImgBB
    with requests.get(file_path, stream=True) as response:
        response.raise_for_status()
        files = {"image": response.content}
        res = requests.post(f"https://api.imgbb.com/1/upload?key={IMGBB_API_KEY}", files=files)

    if res.status_code == 200:
        extension_url = res.json()["data"]["image"]["url"]
        update.message.reply_text(extension_url)
    else:
        update.message.reply_text("Upload failed! Please try again.")

    # Delete "Uploading..."
    context.bot.delete_message(chat_id=status_message.chat_id, message_id=status_message.message_id)


def main():
    updater = Updater(TELEGRAM_BOT_TOKEN)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("authorise", authorise))
    dispatcher.add_handler(CommandHandler("unauthorise", unauthorise))
    dispatcher.add_handler(MessageHandler(Filters.photo | Filters.document, handle_media))

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
