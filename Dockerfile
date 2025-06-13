# Dùng Python 3.12 ổn định (3.12.3 là bản mới nhất tính đến hiện tại)
FROM python:3.12

# Làm việc trong thư mục /app
WORKDIR /app

# Copy toàn bộ code vào container
COPY . /app/

# Cài các thư viện hệ thống cần thiết
RUN apt-get update && apt-get install -y \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Cài các thư viện Python
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Chạy migrate và collectstatic trong lúc build
RUN python manage.py migrate && \
    python manage.py collectstatic --noinput

# Mở cổng 8000 cho container
EXPOSE 8000

# Chạy ứng dụng Django bằng Gunicorn (chuẩn production)
CMD ["gunicorn", "ETMD.wsgi:application", "--bind", "0.0.0.0:8000"]
