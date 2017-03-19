FROM gcr.io/google-appengine/python

# Create a virtualenv for the application dependencies.
RUN virtualenv -p python3.5 /env

# Set virtualenv environment variables. This is equivalent to running
# source /env/bin/activate. This ensures the application is executed within
# the context of the virtualenv and will have access to its dependencies.
ENV VIRTUAL_ENV /env
ENV PATH /env/bin:$PATH

# Requirements have to be pulled and installed here, otherwise caching won't work
COPY requirements.txt /app/requirements.txt

RUN pip install -r /app/requirements.txt \
    && groupadd -r app \
    && useradd -r -g app app

COPY . /app
RUN chown -R app /app

COPY ./compose/entrypoint.sh /entrypoint.sh
RUN sed -i 's/\r//' /entrypoint.sh \
    && chmod +x /entrypoint.sh \
    && chown app /entrypoint.sh \
    && mkdir /cert

WORKDIR /app
ENV PYTHONPATH /app

ENTRYPOINT ["/entrypoint.sh"]
