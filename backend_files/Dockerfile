# Use a minimal Python 3.11 base image (same Python version as the Colab runtime used to train the model)
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the dependencies file first, so the installed packages are cached between builds
COPY requirements.txt .

# Install the Python dependencies without keeping the pip cache, to keep the image small
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code and the serialized model into the container
COPY . .

# Expose the port the API runs on
EXPOSE 7860

# Start the Flask app with Gunicorn
# - "-w 4": uses 4 worker processes for handling requests
# - "-b 0.0.0.0:7860": binds the server to port 7860 on all network interfaces
# - "app:superkart_api": runs the Flask app (superkart_api) from the app.py file
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:7860", "app:superkart_api"]
