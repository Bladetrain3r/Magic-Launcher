# Magic Launcher Docker Image
FROM python:3.9-slim

# Install tkinter and X11 dependencies
RUN apt-get update && apt-get install -y \
    python3-tk \
    x11-apps \
    # xdg-utils \
    lynx \
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
# RUN update-alternatives --set x-www-browser /usr/bin/lynx

RUN echo "export DISPLAY=:0" >> /etc/profile
RUN echo "export PYTHONUNBUFFERED=1" >> /etc/profile

# Ensure the X11 display is accessible

# Set up unprivileged user for security
# RUN useradd -m magicuser
# USER magicuser
# Privileged user for demo purposes, DELETE THIS if copying this Dockerfile for production use

# If installing from a lone dockerfile
# RUN git clone https://github.com/Bladetrain3r/Magic-Launcher.git /root/.local/share/Magic-Launcher && \
#     echo 'alias mlmain="python3 ~/.local/share/Magic-Launcher/launcher/app.py"' >> ~/.bashrc

# If installing from a cloned copy of the repository

RUN mkdir -p /root/.config/launcher
COPY --chown=root:root . /root/.local/share/Magic-Launcher/
RUN chmod +x /root/.local/share/Magic-Launcher/launcher/app.py
COPY --chown=root:root ./launcher/config/demo.json /root/.config/launcher/shortcuts.json

WORKDIR /root/.local/share/Magic-Launcher/

# Set up environment
ENV DISPLAY=:0
ENV PYTHONUNBUFFERED=1

# Default command
CMD ["python3", "/root/.local/share/Magic-Launcher/launcher/app.py"]

# Build with: docker build -t magic-launcher:latest .
# Run with: docker run -it --rm -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix -v $HOME/.config/launcher:/root/.config/launcher magic-launcher
# Isolate Config Directory: docker run -it --rm -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix --device /dev/snd magic-launcher