# Use the official Python image from the Docker Hub
FROM python:3.9-slim

# Set up environment variables for Python
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update \
  && apt-get -y install default-jre

# Set the working directory inside the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 5000 for Flask
EXPOSE 5000

# Define environment variable
ENV FLASK_APP=60_month.py

# Run app.py when the container launches
CMD ["flask", "run", "--host=0.0.0.0"]
