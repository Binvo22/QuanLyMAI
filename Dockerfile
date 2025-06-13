# Dùng Python 3.12 ổn định
FROM python:3.12

WORKDIR /app
COPY . /app/

RUN apt-get update && apt-get install -y \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Mở cổng 8000
EXPOSE 8000

# CMD chạy Gunicorn khi container khởi động
CMD ["gunicorn", "ETMD.wsgi:application", "--bind", "0.0.0.0:8000"]
