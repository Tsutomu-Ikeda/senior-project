FROM python:3.9-buster as builder

WORKDIR /opt/app

COPY requirements.txt /opt/app
RUN pip3 install -r requirements.txt

FROM python:3.9-slim-buster as runner

WORKDIR /app
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages

RUN apt update \
  && apt install -y libxml2 libtiff5-dev libjpeg62-turbo-dev zlib1g-dev libfreetype6-dev liblcms2-dev libwebp-dev libopenjp2-7 libxcb1 \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

RUN useradd -r -s /bin/false geventusr
RUN mkdir -p /opt/app/src/logs/app_logs
RUN touch /opt/app/src/logs/server.log
RUN chown -R geventusr /opt/app/src/logs

COPY ./src/main.py ./src/constants.py ./src/utils.py /app/

USER geventusr

CMD ["python", "-u", "main.py"]
