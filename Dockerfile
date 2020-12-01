FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

COPY ./requirements.txt /requirements.txt

RUN pip install -r /requirements.txt

RUN apt-get update
RUN apt-get install postgresql-client --yes

COPY ./app /app/app
COPY ./prestart.sh /app/prestart.sh

