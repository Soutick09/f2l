FROM python:3.9

# Set working directory
WORKDIR /app

# Copy bot files
COPY bot.py /app/bot.py

# Install dependencies
RUN pip install telethon requests

# Run the bot
CMD ["python", "bot.py"]
