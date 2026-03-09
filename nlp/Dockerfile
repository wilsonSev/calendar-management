FROM python:3.12-slim

WORKDIR /app/nlp

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY nlp/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY nlp /app/nlp

EXPOSE 50052

CMD ["python", "grpc_server.py"]