# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /usr/src/app

# Copy the requirements file into the container
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container
COPY . .

ENV TELEGRAM_BOT_TOKEN=7674446706:AAHk4_GOmE0H2XlWocBH_Yt-YXBLBF0n_o8
ENV IMGBB_API_KEY=741ef2b341b26c4341f929c2356e4e88
ENV OWNER_ID=5827289728
ENV LOG_CHANNEL_ID=-1002332346887
ENV MONGO_URI=mongodb+srv://jimiva5550:jimiva5550@cluster0.hy7t1.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0

# Ensure bot.py has executable permissions
RUN chmod +x bot.py

# Define the default command to run the bot
CMD ["python", "bot.py"]
