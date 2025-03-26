# BUILD STAGE
# Official Python
FROM python:3.10-slim AS builder

# Create app directory
RUN mkdir /app

# Set app as working directory
WORKDIR /app

# Set envs
# Prevent pyc files to disk
ENV PYTHONDONTWRITEBYTECODE=1
# Prevent buffering stdout and stderr
ENV PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get -y install libpq-dev gcc pkg-config default-libmysqlclient-dev

# Upgrade pip
RUN pip install --upgrade pip

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# PRODUCTION STAGE
FROM python:3.10-slim

RUN useradd -m -r appuser && \
    mkdir /app && \
    chown -R appuser /app

# Copy from builder stage
COPY --from=builder /usr/local/lib/python3.10/site-packages/ /usr/local/lib/python3.10/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

# Set working directory
WORKDIR /app

# Copy application code
COPY --chown=appuser:appuser . .

# Set envs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

USER appuser

EXPOSE 8000

# Start application using gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "homepagev3_back.wsgi:application"]