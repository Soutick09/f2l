import os
import time
import requests
import psutil
import logging
from datetime import datetime
from telethon import TelegramClient, events

# Hardcoded API credentials
API_ID = 28450765  # Replace with your API ID
API_HASH = "36f00f11f9d5c65e69b81fd804453a93"  # Replace with your API Hash
BOT_TOKEN = "7674446706:AAHk4_GOmE0H2XlWocBH_Yt-YXBLBF0n_o8"  # Replace with your bot token
IMGBB_API_KEY = "741ef2b341b26c4341f929c2356e4e88"  # Replace with your ImgBB API key
LOG_CHANNEL = -1002332346887  # Replace with your log channel ID
ADMINS = [5827289728]  # Replace with admin user IDs
BANNED_USERS = set()  # Store banned users

# Initialize bot client
bot = TelegramClient('bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# Logging setup
logging.basicConfig(level=logging.INFO)

# Bot start time
START_TIME = time.time()

# Function to get bot uptime
def get_uptime():
    uptime_seconds = int(time.time() - START_TIME)
    hours, remainder = divmod(uptime_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours}h {minutes}m {seconds}s"

# Function to get VPS stats
def get_vps_stats():
    cpu_usage = psutil.cpu_percent(interval=1)
    ram_usage = psutil.virtual_memory().percent
    disk_usage = psutil.disk_usage('/').percent
    return f"💻 CPU: {cpu_usage}%\n🖥 RAM: {ram_usage}%\n📂 Disk: {disk_usage}%"

# Function to upload image to ImgBB
def upload_image(file_path):
    with open(file_path, "rb") as img:
        response = requests.post(
            "https://api.imgbb.com/1/upload",
            params={"key": IMGBB_API_KEY},
            files={"image": img}
        )
    os.remove(file_path)  # Delete local file after upload
    return response.json().get("data", {}).get("url")

# Check if user is an admin
def is_admin(user_id):
    return user_id in ADMINS

# Handle /start command
@bot.on(events.NewMessage(pattern="/start"))
async def start(event):
    user = event.sender
    await event.respond(f"👋 Hello {user.first_name}! Send me an image, and I'll give you a permanent link.")

    # Log user start event
    log_msg = f"🚀 New User Started Bot\n👤 User: @{user.username} (ID: {user.id})"
    await bot.send_message(LOG_CHANNEL, log_msg)

# Handle image uploads
@bot.on(events.NewMessage(func=lambda e: e.photo))
async def handle_image(event):
    user = event.sender

    # Check if user is banned
    if user.id in BANNED_USERS:
        await event.reply("🚫 You are banned from using this bot.")
        return

    msg = await event.reply("🔄 Uploading image...")

    # Save the image file
    photo = await event.download_media()

    # Upload to ImgBB
    image_url = upload_image(photo)

    if image_url:
        # Send the result
        buttons = [[{"text": "📋 Copy Link", "url": image_url}]]
        await event.respond(f"✅ Image Uploaded!\n🔗 [Click Here]({image_url})", buttons=buttons)
    else:
        await event.respond("❌ Failed to upload image. Please try again.")

    # Delete the uploading message
    await msg.delete()

    # Log upload
    log_msg = f"🖼 New Image Upload\n👤 User: @{user.username} (ID: {user.id})\n📷 Image: {image_url}"
    await bot.send_message(LOG_CHANNEL, log_msg)

# Admin commands
@bot.on(events.NewMessage(pattern="/ban (\d+)"))
async def ban_user(event):
    if is_admin(event.sender_id):
        user_id = int(event.pattern_match.group(1))
        BANNED_USERS.add(user_id)
        await event.respond(f"🚫 User {user_id} has been banned.")
    else:
        await event.respond("❌ You are not an admin!")

@bot.on(events.NewMessage(pattern="/unban (\d+)"))
async def unban_user(event):
    if is_admin(event.sender_id):
        user_id = int(event.pattern_match.group(1))
        BANNED_USERS.discard(user_id)
        await event.respond(f"✅ User {user_id} has been unbanned.")
    else:
        await event.respond("❌ You are not an admin!")

@bot.on(events.NewMessage(pattern="/stats"))
async def stats(event):
    if is_admin(event.sender_id):
        uptime = get_uptime()
        vps_stats = get_vps_stats()
        await event.respond(f"📊 **Bot Stats**\n⏳ Uptime: {uptime}\n\n{vps_stats}")
    else:
        await event.respond("❌ You are not an admin!")

@bot.on(events.NewMessage(pattern="/broadcast (.+)"))
async def broadcast(event):
    if is_admin(event.sender_id):
        message = event.pattern_match.group(1)
        await bot.send_message("me", message)  # Replace with actual broadcast logic
        await event.respond("📢 Broadcast sent!")
    else:
        await event.respond("❌ You are not an admin!")

# Start the bot
print("🤖 Bot is running...")
bot.run_until_disconnected()
