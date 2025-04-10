FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt ./

RUN apt-get update && \
    apt-get install -y ffmpeg libsm6 libxext6 v4l-utils libv4l-dev && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["gunicorn", "-c", "gunicorn_config.py", "--logger-class=gunicorn_color.Logger", "--chdir=src", "main:app"]

