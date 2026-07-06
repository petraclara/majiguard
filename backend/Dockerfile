FROM python:3.12-slim

# Install uv for fast dependency management
RUN pip install --no-cache-dir uv==0.8.13

WORKDIR /code

# Copy requirements and install
COPY requirements.txt ./
RUN uv pip install --system --no-cache -r requirements.txt

# Copy source code
COPY ./app ./app
COPY ./main.py ./

# Create data directory for SQLite database
RUN mkdir -p app/data

EXPOSE 8000

CMD ["python", "main.py"]
