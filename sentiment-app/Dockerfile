FROM python:alpine3.7
COPY . /app
WORKDIR /app
RUN python3 -m pip install -r requirements.txt --no-cache-dir
EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]