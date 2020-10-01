FROM python:3.7
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
ENV http_proxy=
ENV https_proxy=
ENV no_proxy=
COPY . .
CMD uvicorn main:app --host 0.0.0.0 --port 5000