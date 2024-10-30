# Use the official Python image from the Docker Hub
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and application code into the container
COPY requirements.txt ./
COPY app.py ./

# Create templates directory and copy index.html into it
RUN mkdir templates
COPY templates/index.html templates/

# Install any required packages
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port that the app runs on
EXPOSE 5000

# Command to run the application
CMD ["python", "app.py"]
