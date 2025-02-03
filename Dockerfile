# Use official Python image
FROM python:3.10

# Set the working directory
WORKDIR /app

# Copy all files to the container
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables (optional, use .env file instead)
ENV TELEGRAM_BOT_TOKEN=""
ENV IMGBB_API_KEY=""
ENV OWNER_ID=""
ENV LOG_CHANNEL_ID=""

# Run the bot
CMD ["python", "bot.py"]
