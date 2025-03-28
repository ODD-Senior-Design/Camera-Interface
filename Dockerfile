FROM python:3.13
COPY . /app
RUN pip install -r requirements.txt
CMD [ "gunicorn", "main:main" ]