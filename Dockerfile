# Use Python 3.7 for compatibility with Pandas 0.24.2 and TF 1.x
FROM python:3.7-slim

# Prevents warnings from pip
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

COPY . .

# The Flask app runs on port 5000
EXPOSE 5000

CMD ["python", "food_volume_estimation_app.py"]

