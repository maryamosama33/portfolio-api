FROM python:3.14.3-slim

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

CMD ["adk", "web", "--host", "0.0.0.0", "--port", "8001"]