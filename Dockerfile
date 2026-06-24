# 1. Use a lightweight official Python runtime as the parent image
FROM python:3.12-slim

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Install system dependencies required for compilation (e.g., for database drivers like psycopg2/asyncpg)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 4. Copy the requirements file first to leverage Docker's caching mechanism
COPY requirements.txt .

# 5. Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy the rest of the microservice codebase into the container
COPY . .

# Copy shared security module from auth_service
COPY auth_service/app /auth_service/app

# 7. Expose the port that this microservice runs on (e.g., 8001 for accounts_service)
# Note: EXPOSE is informational; Docker Compose will handle port mapping.
EXPOSE 8001

# 8. Command to run the application using Uvicorn
# We bind to 0.0.0.0 so that the container can accept external requests.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
