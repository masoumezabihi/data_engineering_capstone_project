# Use Python + OpenJDK 11
FROM openjdk:11-jdk-slim

# Install Python 3 and pip
RUN apt-get update && \
    apt-get install -y python3 python3-pip procps && \
    ln -s /usr/bin/python3 /usr/bin/python && \
    rm -rf /var/lib/apt/lists/*

# Set JAVA_HOME for PySpark
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64

WORKDIR /usr/app

# Copy requirements and install
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy consumer code
COPY . .

# Run the Spark consumer
CMD ["python", "consumer.py"]
