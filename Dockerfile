# Stage 1: Build Stage
FROM python:3.8-alpine AS build

# Install system dependencies
RUN apk update && \
    apk add --no-cache \
    build-base \
    libffi-dev \
    postgresql-dev

# Install Pipenv
RUN pip install pipenv

# Create a temporary directory for the build
WORKDIR /build

# Copy Pipfile and Pipfile.lock
COPY Pipfile* /build/

# Install Python dependencies using Pipenv and remove Pipenv, pip, and setuptools
RUN pipenv install --deploy --system --ignore-pipfile && \
    pip uninstall pipenv pip setuptools build-base -y && \
    rm -rf /root/.cache

# Copy the application code into the container
COPY src /build

# Stage 2: Production Stage
FROM python:3.9-alpine AS production

# Set environment variables
ENV HOST=http://159.203.50.162 \
    TOKEN=d6e33ac9ad141a18af77 \
    T_MAX=20 \
    T_MIN=10 \
    DATABASE_URL=postgresql://user02eq8:5ZBBwc9GvESZLKhg@157.230.69.113:5432/db02eq8

# Install libpq and other necessary dependencies
RUN apk update && \
    apk add --no-cache \
    libpq

# Remove unnecessary packages
RUN apk del build-base libffi-dev postgresql-dev expat

# Copy dependencies from the build stage
COPY --from=build /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY --from=build /build /app

# Remove pip
RUN apk del python3 && \
    rm -rf /var/cache/apk/* && \
    rm -rf /usr/local/bin/pip*

# Set the working directory
WORKDIR /app

# Run the application
CMD ["python", "main.py"]
