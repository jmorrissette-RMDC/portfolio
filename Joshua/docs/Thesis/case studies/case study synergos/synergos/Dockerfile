# Synergos - The First Autonomous Multi-Agent Creation
# Built entirely by AI collaboration through Sultan's Blueprint
# October 16, 2025

FROM python:3.9-slim

# Install system dependencies for Tkinter and X11
RUN apt-get update && apt-get install -y \
    python3-tk \
    sqlite3 \
    x11-apps \
    xauth \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy application files
COPY main.py .
COPY task_manager.py .
COPY synthesized_application.py .
COPY test_application.py .
COPY requirements.txt .

# Install Python dependencies (if any)
RUN pip install --no-cache-dir -r requirements.txt || true

# Documentation files
COPY README.md .
COPY 01_requirements_spec.md ./docs/
COPY 02_approach_overview.md ./docs/
COPY 03_design_principles.md ./docs/

# Create data directory for SQLite database
RUN mkdir -p /app/data

# Set environment variables for X11
ENV DISPLAY=:0

# Historic metadata
LABEL org.opencontainers.image.title="Synergos" \
      org.opencontainers.image.description="First application built entirely by AI collaboration" \
      org.opencontainers.image.created="2025-10-16" \
      org.opencontainers.image.authors="Sultan's Blueprint Team (6 LLMs)" \
      org.opencontainers.image.source="https://github.com/rmdevpro/Joshua" \
      org.opencontainers.image.documentation="https://github.com/rmdevpro/Joshua/tree/main/synergos"

# Run the application
CMD ["python3", "main.py"]