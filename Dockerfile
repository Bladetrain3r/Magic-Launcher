# Magic Launcher Docker Image
FROM python:3.9-slim

# Install tkinter and X11 dependencies
RUN apt-get update && apt-get install -y \
    python3-tk \
    x11-apps \
    xdg-utils \
    firefox-esr \
    # Basic utilities that shortcuts might use
    curl \
    wget \
    vim \
    nano \
    htop \
    # Cleanup
    && rm -rf /var/lib/apt/lists/*

# Install Pillow for BMP support
RUN pip install --no-cache-dir Pillow

# Create app directory
WORKDIR /app

# Copy launcher files
COPY launcher/ /app/launcher/

# Create config directory structure
RUN mkdir -p /root/.config/launcher/icons

# Optional: Copy example configs
# COPY examples/docker/shortcuts.json /root/.config/launcher/

# Set up environment
ENV DISPLAY=:0
ENV PYTHONUNBUFFERED=1

# Create a startup script
RUN echo '#!/bin/bash\ncd /app/launcher && python3 app.py' > /start.sh && \
    chmod +x /start.sh

# Default command
CMD ["/start.sh"]

# Build with: docker build -t magic-launche:latest .
# Run with: docker run -it --rm -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix -v $HOME/.config/launcher:/root/.config/launcher magic-launcher
# Isolate Config Directory: docker run -it --rm -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix magic-launcher