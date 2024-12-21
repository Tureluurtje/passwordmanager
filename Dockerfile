# Use the official Python image from the Docker Hub
FROM python:3.10-slim

# Install dependencies for tkinter
RUN apt-get update && apt-get install -y \
    python3-tk \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev

# Set the working directory
WORKDIR /app/passwordmanager

# Copy the requirements file
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port the app runs on
EXPOSE 5000

# Run the application
ENTRYPOINT [ "python" ]
CMD ["api/app.py"]