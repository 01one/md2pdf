FROM python:3.11-slim

# system dependencies for WeasyPrint
RUN apt-get update && apt-get install -y --no-install-recommends \
    gir1.2-pango-1.0 \
    gir1.2-glib-2.0 \
    libpango-1.0-0 \
    libcairo2 \
    libgdk-pixbuf2.0-0 \
    libgirepository1.0-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*


WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "app.py"]
