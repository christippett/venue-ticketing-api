FROM python:3.5

ENV PYTHONUNBUFFERED 1

# Requirements have to be pulled and installed here, otherwise caching won't work
COPY ./requirements.txt /requirements.txt

RUN pip install -r /requirements.txt \
    && groupadd -r app \
    && useradd -r -g app app

COPY . /app
RUN chown -R app /app

COPY ./compose/gunicorn.sh /gunicorn.sh
RUN sed -i 's/\r//' /gunicorn.sh \
    && chmod +x /gunicorn.sh \
    && chown app /gunicorn.sh

WORKDIR /app
ENV PYTHONPATH /app

CMD ["/gunicorn.sh"]
