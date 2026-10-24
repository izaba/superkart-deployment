# Use a minimal Python 3.11 base image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the dependencies file first, so the installed packages are cached between builds
COPY requirements.txt .

# Install the Python dependencies without keeping the pip cache, to keep the image small
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Streamlit app into the container
COPY . .

# Expose the port Streamlit runs on
EXPOSE 8501

# Start the Streamlit app
# - "--server.address=0.0.0.0": makes the app reachable from outside the container
# - "--server.port=8501": runs the app on port 8501
# - "--server.enableXsrfProtection=false" and "--server.enableCORS=false": allow file uploads through the Codespaces forwarded URL
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501", "--server.enableXsrfProtection=false", "--server.enableCORS=false"]
