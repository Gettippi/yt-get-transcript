# Use a lightweight Python image
FROM python:3.9-slim

# Install ffmpeg
# ffmpeg only required if downloading videos
RUN apt-get update && \
    apt-get install -y ffmpeg && \ 
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy the requirements file to the container
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Flask app to the container
COPY app.py .

# Expose the port the app runs on
EXPOSE 5000

# Command to run the Flask app
CMD ["python", "app.py"]
