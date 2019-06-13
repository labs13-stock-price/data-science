FROM python:alpine3.7
COPY . /app
WORKDIR /app
RUN \
    apk add make automake gcc g++ subversion libffi-dev openssl-dev libxml2-dev libxslt-dev python3-dev && \
    python3 -m pip install -r requirements.txt --no-cache-dir
EXPOSE 8070
CMD ["sh", "./run_app.sh"]