FROM python:3.9-buster as builder

WORKDIR /opt/app

RUN apt update \
  && apt install -y portaudio19-dev

COPY requirements.txt /opt/app
RUN pip3 install -r requirements.txt

FROM python:3.9-slim-buster as runner

WORKDIR /app
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY --from=builder /usr/local/bin/uwsgi /usr/local/bin/uwsgi

RUN apt update \
  && apt install -y libxml2 portaudio19-dev \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

RUN useradd -r -s /bin/false uwsgiusr
RUN mkdir -p /opt/app/src/logs/app_logs
RUN touch /opt/app/src/logs/server.log
RUN chown -R uwsgiusr /opt/app/src/logs

COPY ./src/main.py ./src/uwsgi.ini /app/

USER uwsgiusr

CMD ["uwsgi", "--ini", "/app/uwsgi.ini"]
