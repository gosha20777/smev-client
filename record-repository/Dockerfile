FROM python:3.7
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
ENV NO_PROXY "127.0.0.1,localhost"
CMD uvicorn server:app --host 0.0.0.0 --port 5000
