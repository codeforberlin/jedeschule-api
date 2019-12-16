FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

ADD ./requirements.txt /requirements.txt

RUN pip install -r /requirements.txt

COPY ./app /app/app
COPY ./prestart.sh /app/prestart.sh
COPY ./test_connection.py /app

