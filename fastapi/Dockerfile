FROM python:3.10-slim
WORKDIR /usr/src/app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
ENV PYTHONPATH=/usr/src/app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]