import os
import requests
import logging
from telethon import TelegramClient, events

# Hardcoded API credentials
API_ID = 28450765  # Replace with your API ID
API_HASH = "36f00f11f9d5c65e69b81fd804453a93"  # Replace with your API Hash
BOT_TOKEN = "7674446706:AAHk4_GOmE0H2XlWocBH_Yt-YXBLBF0n_o8"  # Replace with your bot token
IMGBB_API_KEY = "741ef2b341b26c4341f929c2356e4e88"  # Replace with your ImgBB API key
LOG_CHANNEL = -1002332346887  # Replace with your log channel ID
ADMINS = [5827289728]  # Replace with admin user IDs

# Initialize bot client
bot = TelegramClient('bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# Logging setup
logging.basicConfig(level=logging.INFO)

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

# Function to check if user is an admin
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
    msg = await event.reply("🔄 Uploading image...")

    # Save the image file
    photo = await event.download_media()

    # Upload to ImgBB
    image_url = upload_image(photo)
    
    # Send the result
    buttons = [[{"text": "📋 Copy Link", "url": image_url}]]
    await event.respond(f"✅ Image Uploaded!\n🔗 [Click Here]({image_url})", buttons=buttons)
    
    # Delete the uploading message
    await msg.delete()

    # Log upload
    log_msg = f"🖼 New Image Upload\n👤 User: @{user.username} (ID: {user.id})\n📷 Image: {image_url}"
    await bot.send_message(LOG_CHANNEL, log_msg)

# Admin commands
@bot.on(events.NewMessage(pattern="/ban (.+)"))
async def ban_user(event):
    if is_admin(event.sender_id):
        user_id = int(event.pattern_match.group(1))
        ADMINS.append(user_id)  # Add to banned list
        await event.respond(f"🚫 User {user_id} has been banned.")
    else:
        await event.respond("❌ You are not an admin!")

@bot.on(events.NewMessage(pattern="/unban (.+)"))
async def unban_user(event):
    if is_admin(event.sender_id):
        user_id = int(event.pattern_match.group(1))
        ADMINS.remove(user_id)
        await event.respond(f"✅ User {user_id} has been unbanned.")
    else:
        await event.respond("❌ You are not an admin!")

@bot.on(events.NewMessage(pattern="/stats"))
async def stats(event):
    if is_admin(event.sender_id):
        await event.respond(f"📊 Total users: {len(ADMINS)} (Tracking not fully implemented)")
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
