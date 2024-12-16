# Use official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy files to the container
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run the bot
CMD ["python", "bot.py"]
