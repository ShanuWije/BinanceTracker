# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container
COPY . /app/

# Create and set proper permissions for the .streamlit directory
RUN mkdir -p /app/.streamlit
COPY .streamlit/config.toml /app/.streamlit/

# Install the required dependencies
RUN pip install --no-cache-dir streamlit pandas numpy plotly requests

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variable
ENV STREAMLIT_SERVER_PORT=5000
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Run streamlit when the container launches
CMD ["streamlit", "run", "app.py"]