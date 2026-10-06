FROM python:3.13-slim

WORKDIR /app
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY portfolio_bot ./portfolio_bot

EXPOSE 8001
CMD ["adk", "web", "--host", "0.0.0.0", "--port", "8001"]
