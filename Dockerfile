FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY migrate.py .

CMD ["python", "migrate.py", \
     "--old", "${OLD_MONGODB_URI}", \
     "--new", "${NEW_MONGODB_URI}", \
     "--batch", "5000"]
