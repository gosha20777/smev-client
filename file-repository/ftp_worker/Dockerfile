FROM python:3.7
WORKDIR /app
RUN pip install rq redis
COPY . .
CMD rq worker --url redis://redis:6378 test_queue
