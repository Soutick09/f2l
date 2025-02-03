# Use official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install necessary system packages
RUN apt update && apt install -y curl

# Install Docker (required for DeepStack)
RUN curl -fsSL https://get.docker.com | sh

# Copy bot files to the container
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Start DeepStack in the background
RUN docker run --rm -d -p 5000:5000 deepquestai/deepstack --nsfw

# Run the bot
CMD ["python", "bot.py"]
