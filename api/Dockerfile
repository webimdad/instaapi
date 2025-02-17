# Use an official Python runtime as a parent image
FROM python:3.9

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port Flask is running on
EXPOSE 8080

# Command to run the Flask app
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "wsgi:app"]
