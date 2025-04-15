FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY main.py .
COPY triggerAndResponse.py .
COPY prefixAndResponse.py .
CMD ["python", "main.py"]