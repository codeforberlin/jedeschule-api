FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

COPY ./requirements.txt /requirements.txt

RUN pip install -r /requirements.txt

RUN apt-get update
RUN apt-get install postgresql-client-11 --yes

COPY ./app /app/app
COPY ./prestart.sh /app/prestart.sh
COPY ./test_connection.py /app

