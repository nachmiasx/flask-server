FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

ENV GOOGLE_VISION_KEY_PATH=/app/services/google-vision-key.json

# Set the command to run Alembic upgrade before starting the app
CMD alembic upgrade head && python app.py

EXPOSE 5001
