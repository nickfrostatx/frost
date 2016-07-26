FROM python:3.5

WORKDIR /app

RUN pip install uwsgi

RUN useradd -r app
RUN CHMOD 644 /config/config.py

ADD . /app
RUN pip install /app

USER app

EXPOSE 8000

CMD ["uwsgi", "-s", "0.0.0.0:8000", "-w", "frost.wsgi:application"]
