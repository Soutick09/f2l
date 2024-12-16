import os
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackContext,
)
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Environment variables
TELEGRAM_BOT_TOKEN = os.getenv("7778310816:AAHkhL5Q1Kv1qNM4UVKdyKIcUDoB3BXtc_c")
IMGBB_API_KEY = os.getenv("741ef2b341b26c4341f929c2356e4e88")
OWNER_ID = int(os.getenv("5827289728"))  # Your Telegram ID as an integer

# Authorized users list
authorized_users = set()


async def start(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if user_id not in authorized_users:
        await update.message.reply_text("Access Denied! DM @Soutick_09 to use this Bot.")
    else:
        keyboard = [[InlineKeyboardButton("Developer", url="https://t.me/Soutick_09")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Made With ♥️ By Soutick", reply_markup=reply_markup)


async def authorise(update: Update, context: CallbackContext):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("Only the bot owner can use this command.")
        return

    if len(context.args) != 1:
        await update.message.reply_text("Usage: /authorise <user_id_or_username>")
        return

    target = context.args[0]
    try:
        user_id = int(target)
    except ValueError:
        user_id = (await context.bot.get_chat(target)).id

    authorized_users.add(user_id)
    await context.bot.send_message(chat_id=user_id, text="Congratulations 🎉! You are now authorized.")
    await update.message.reply_text(f"User {target} has been authorized.")


async def unauthorise(update: Update, context: CallbackContext):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("Only the bot owner can use this command.")
        return

    if len(context.args) != 1:
        await update.message.reply_text("Usage: /unauthorise <user_id_or_username>")
        return

    target = context.args[0]
    try:
        user_id = int(target)
    except ValueError:
        user_id = (await context.bot.get_chat(target)).id

    if user_id in authorized_users:
        authorized_users.remove(user_id)
        await context.bot.send_message(chat_id=user_id, text="Alas 😭! You have been unauthorized.")
        await update.message.reply_text(f"User {target} has been unauthorized.")
    else:
        await update.message.reply_text(f"User {target} was not authorized.")


async def handle_media(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if user_id not in authorized_users:
        await update.message.reply_text("Access Denied! DM @Soutick_09 to use this Bot.")
        return

    file = update.message.photo[-1] if update.message.photo else update.message.document
    file_path = await context.bot.get_file(file.file_id)

    # Log "Uploading..."
    status_message = await update.message.reply_text("Uploading...")

    # Upload to ImgBB
    with requests.get(file_path.file_path, stream=True) as response:
        response.raise_for_status()
        files = {"image": response.content}
        res = requests.post(f"https://api.imgbb.com/1/upload?key={IMGBB_API_KEY}", files=files)

    if res.status_code == 200:
        extension_url = res.json()["data"]["image"]["url"]
        await update.message.reply_text(extension_url)
    else:
        await update.message.reply_text("Upload failed! Please try again.")

    # Delete "Uploading..."
    await context.bot.delete_message(chat_id=status_message.chat_id, message_id=status_message.message_id)


def main():
    # Create the bot application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("authorise", authorise))
    application.add_handler(CommandHandler("unauthorise", unauthorise))
    application.add_handler(MessageHandler(filters.PHOTO | filters.Document.ALL, handle_media))

    # Start the bot
    application.run_polling()


if __name__ == "__main__":
    main()
