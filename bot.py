import os
import requests
import json
import sys
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
IMGBB_API_KEY = os.getenv("IMGBB_API_KEY")
DEEPSTACK_URL = os.getenv("DEEPSTACK_URL")  # Local NSFW API
OWNER_ID = int(os.getenv("OWNER_ID"))
LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID"))

# User Data
users = set()
warnings = {}
banned_users = set()

# Start Command
async def start(update: Update, context: CallbackContext):
    user = update.effective_user
    users.add(user.id)  # Store user ID
    await update.message.reply_text("Welcome! Send an image to upload.")
    await context.bot.send_message(LOG_CHANNEL_ID, f"👤 New user: [{user.full_name}](tg://user?id={user.id})", parse_mode="Markdown")

# Ban System
async def ban(update: Update, context: CallbackContext):
    if update.effective_user.id != OWNER_ID:
        return
    if not context.args:
        await update.message.reply_text("Usage: /ban <user_id>")
        return
    user_id = int(context.args[0])
    banned_users.add(user_id)
    await update.message.reply_text(f"🚫 User {user_id} has been banned!")

async def unban(update: Update, context: CallbackContext):
    if update.effective_user.id != OWNER_ID:
        return
    if not context.args:
        await update.message.reply_text("Usage: /unban <user_id>")
        return
    user_id = int(context.args[0])
    banned_users.discard(user_id)
    await update.message.reply_text(f"✅ User {user_id} has been unbanned!")

# NSFW Detection (Local AI)
async def check_nsfw(image_path):
    files = {"image": open(image_path, "rb")}
    response = requests.post(DEEPSTACK_URL, files=files).json()
    return response["nsfw"] > 0.7  # NSFW threshold

# Handle Media Upload
async def handle_media(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if user_id in banned_users:
        await update.message.reply_text("🚫 You are banned from using this bot.")
        return

    file = update.message.photo[-1] if update.message.photo else update.message.document
    file_info = await context.bot.get_file(file.file_id)
    image_path = f"{user_id}.jpg"
    await file_info.download_to_drive(image_path)

    # NSFW Check
    if await check_nsfw(image_path):
        warnings[user_id] = warnings.get(user_id, 0) + 1
        os.remove(image_path)  # Delete NSFW image
        if warnings[user_id] >= 3:
            banned_users.add(user_id)
            await update.message.reply_text("🚨 You have been banned for sending NSFW images!")
        else:
            await update.message.reply_text(f"⚠️ Warning {warnings[user_id]}/3: NSFW content is not allowed!")
        return

    # Upload to ImgBB
    with open(image_path, "rb") as img:
        res = requests.post(f"https://api.imgbb.com/1/upload?key={IMGBB_API_KEY}", files={"image": img})

    os.remove(image_path)  # Delete local file

    if res.status_code == 200:
        image_url = res.json()["data"]["image"]["url"]
        await update.message.reply_text(f"{image_url}")

        # Forward image to log channel
        await context.bot.send_photo(LOG_CHANNEL_ID, photo=image_url, caption=f"📸 Image from [{update.effective_user.full_name}](tg://user?id={user_id}) (`{user_id}`)", parse_mode="Markdown")
    else:
        await update.message.reply_text("❌ Upload failed! Please try again.")

# Broadcast Message
async def broadcast(update: Update, context: CallbackContext):
    if update.effective_user.id != OWNER_ID:
        return
    if not context.args:
        await update.message.reply_text("Usage: /broadcast <message>")
        return
    message = " ".join(context.args)
    sent_count = 0
    for user_id in users:
        try:
            await context.bot.send_message(user_id, message, parse_mode="Markdown")
            sent_count += 1
        except:
            pass  # Ignore errors
    await update.message.reply_text(f"📢 Broadcast sent to {sent_count} users!")

# Bot Stats
async def stats(update: Update, context: CallbackContext):
    if update.effective_user.id != OWNER_ID:
        return
    await update.message.reply_text(f"📊 Total Users: {len(users)}\n🚫 Banned Users: {len(banned_users)}")

# Restart Bot
async def restart(update: Update, context: CallbackContext):
    if update.effective_user.id != OWNER_ID:
        return
    await update.message.reply_text("🔄 Restarting bot...")
    os.execl(sys.executable, sys.executable, *sys.argv)  # Proper restart

# Main Function
def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Commands
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("ban", ban))
    application.add_handler(CommandHandler("unban", unban))
    application.add_handler(CommandHandler("broadcast", broadcast))
    application.add_handler(CommandHandler("stats", stats))
    application.add_handler(CommandHandler("restart", restart))

    # Media Handling
    application.add_handler(MessageHandler(filters.PHOTO | filters.Document.IMAGE, handle_media))

    # Start bot
    application.run_polling()

if __name__ == "__main__":
    main()
