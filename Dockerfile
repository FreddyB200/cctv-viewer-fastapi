# Use an official, lightweight Python image as a base
FROM python:3.11-slim

# Install dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ffmpeg \
    wget \
    ca-certificates \
    supervisor && \
    rm -rf /var/lib/apt/lists/*

# Install go2rtc
RUN wget -O /usr/local/bin/go2rtc https://github.com/AlexxIT/go2rtc/releases/latest/download/go2rtc_linux_amd64 && \
    chmod +x /usr/local/bin/go2rtc

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file first to leverage Docker's layer caching
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application's code into the container
COPY . .

# Tell Docker that the container will listen on ports
EXPOSE 8000 1984 8554

# Copy supervisor config
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# The command to run when the container starts
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]