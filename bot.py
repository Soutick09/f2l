import os
import requests
import hashlib
from io import BytesIO
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackContext,
)
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
IMGBB_API_KEY = os.getenv("IMGBB_API_KEY")
OWNER_ID = int(os.getenv("OWNER_ID"))
LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID"))  # Log channel for tracking activity

# Store banned users and uploaded file hashes
banned_users = set()
uploaded_hashes = set()


async def start(update: Update, context: CallbackContext):
    keyboard = [[InlineKeyboardButton("Developer", url="https://t.me/Soutick_09")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Made With ♥️ By Soutick", reply_markup=reply_markup)


async def ban(update: Update, context: CallbackContext):
    if update.effective_user.id != OWNER_ID:
        return await update.message.reply_text("Only the bot owner can use this command.")
    
    if not context.args:
        return await update.message.reply_text("Usage: /ban <user_id>")
    
    user_id = int(context.args[0])
    banned_users.add(user_id)
    await update.message.reply_text(f"User {user_id} has been banned.")


async def unban(update: Update, context: CallbackContext):
    if update.effective_user.id != OWNER_ID:
        return await update.message.reply_text("Only the bot owner can use this command.")
    
    if not context.args:
        return await update.message.reply_text("Usage: /unban <user_id>")
    
    user_id = int(context.args[0])
    banned_users.discard(user_id)
    await update.message.reply_text(f"User {user_id} has been unbanned.")


async def stats(update: Update, context: CallbackContext):
    if update.effective_user.id != OWNER_ID:
        return await update.message.reply_text("Only the bot owner can use this command.")
    
    total_users = len(context.application.bot_data.get("users", set()))
    total_uploads = len(uploaded_hashes)
    
    stats_message = f"📊 **Bot Stats**\n\n👥 Users: {total_users}\n📸 Uploaded Images: {total_uploads}"
    await update.message.reply_text(stats_message)


async def restart(update: Update, context: CallbackContext):
    if update.effective_user.id != OWNER_ID:
        return await update.message.reply_text("Only the bot owner can use this command.")
    
    await update.message.reply_text("🔄 Restarting bot...")
    os.execv(__file__, ['python'] + os.sys.argv)


async def handle_media(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if user_id in banned_users:
        return await update.message.reply_text("❌ You are banned from using this bot.")

    file = update.message.photo[-1] if update.message.photo else update.message.document
    file_path = await context.bot.get_file(file.file_id)

    # Log user activity
    mention = f"[{update.effective_user.first_name}](tg://user?id={user_id})"
    log_message = f"📸 Image received from {mention} (`{user_id}`)"
    await context.bot.send_message(LOG_CHANNEL_ID, text=log_message)

    # Download file for NSFW & duplicate detection
    file_data = requests.get(file_path.file_path).content
    file_hash = hashlib.md5(file_data).hexdigest()

    if file_hash in uploaded_hashes:
        return await update.message.reply_text("⚠️ Duplicate image detected. Upload canceled.")

    uploaded_hashes.add(file_hash)

    # Upload Progress Bar
    status_message = await update.message.reply_text("⏳ Uploading...")

    # Upload to ImgBB
    files = {"image": file_data}
    res = requests.post(f"https://api.imgbb.com/1/upload?key={IMGBB_API_KEY}", files=files)

    if res.status_code == 200:
        img_url = res.json()["data"]["image"]["url"]
        await update.message.reply_text(f"✅ Uploaded: {img_url}")
    else:
        await update.message.reply_text("❌ Upload failed! Please try again.")

    await context.bot.delete_message(chat_id=status_message.chat_id, message_id=status_message.message_id)


async def broadcast(update: Update, context: CallbackContext):
    if update.effective_user.id != OWNER_ID:
        return await update.message.reply_text("Only the bot owner can use this command.")
    
    if not context.args:
        return await update.message.reply_text("Usage: /broadcast <message>")
    
    message_text = " ".join(context.args)

    # Retrieve all users from bot_data
    users = context.application.bot_data.get("users", set())

    for user_id in users:
        try:
            await context.bot.send_message(user_id, text=message_text, parse_mode="Markdown")
        except Exception:
            pass  # Ignore errors (e.g., user blocked bot)

    await update.message.reply_text("📢 Broadcast sent to all users.")


def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("ban", ban))
    application.add_handler(CommandHandler("unban", unban))
    application.add_handler(CommandHandler("stats", stats))
    application.add_handler(CommandHandler("restart", restart))
    application.add_handler(CommandHandler("broadcast", broadcast))
    application.add_handler(MessageHandler(filters.PHOTO | filters.Document.ALL, handle_media))

    # Start the bot
    application.run_polling()


if __name__ == "__main__":
    main()
