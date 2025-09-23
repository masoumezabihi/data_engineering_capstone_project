# Dockerfile
FROM python:3.10-slim

WORKDIR /usr/app


ADD ./requirements.txt ./
RUN pip install -r requirements.txt
ADD ./ ./

CMD ["python", "app.py"]