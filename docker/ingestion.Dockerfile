FROM python:3.11-slim

WORKDIR /app
COPY ingestion/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

CMD ["python", "ingestion/load_raw.py"]
