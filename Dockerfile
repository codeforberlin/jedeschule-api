FROM python:3.12

COPY ./requirements.txt /requirements.txt

RUN apt-get update
RUN apt-get install postgresql-client libgeos-dev --yes

RUN pip install -r /requirements.txt


COPY ./app /app/app
COPY ./prestart.sh /app/prestart.sh

CMD ["fastapi", "run", "/app/app/main.py", "--port", "80", "--workers", "4"]
