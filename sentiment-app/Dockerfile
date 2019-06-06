FROM python:alpine3.7
COPY . /app
WORKDIR /app
RUN \
    apk add make automake gcc g++ subversion python3-dev && \
    apk add --no-cache postgresql-libs && \
    apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev && \
    python3 -m pip install -r requirements.txt --no-cache-dir &&\
    apk --purge del .build-deps

EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]