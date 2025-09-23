FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY fraud_exporter.py .
CMD ["python", "fraud_exporter.py"]
