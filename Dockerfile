FROM python:3.13
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt && cd src
CMD [ "gunicorn", "-c", "../deployment/gunicorn_config.py", "--logger-class=gunicorn_color.Logger" , "main:main()" ]
