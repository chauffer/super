FROM python:3.8-alpine

WORKDIR /app
COPY ./requirements.txt /app
RUN apk --virtual=.build-deps add build-base musl-dev git libffi-dev gcc &&\
    apk --virtual=.run-deps add ffmpeg opus chromium chromium-chromedriver && \
    mkdir -p /dependencies && cd /dependencies &&\
    pip install --no-cache-dir -r /app/requirements.txt &&\
    apk --purge del .build-deps

COPY . /app
RUN pip install -e .

ENV PYTHONUNBUFFERED=1
VOLUME /data
CMD python -m super.run
LABEL name=super version=dev
