# Use a Python image from the Docker Hub
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements.txt into the container
COPY requirements.txt .

# Install all the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project into the container
COPY . .

# Expose the port (optional, usually for web apps, not needed for bots)
EXPOSE 5000

# Run the bot when the container starts
CMD ["python", "bot.py"]
