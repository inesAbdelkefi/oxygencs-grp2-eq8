# Build stage
FROM python:3.8-slim AS build

WORKDIR /app

# Copy only the Pipfile and Pipfile.lock
COPY Pipfile Pipfile.lock /app/
COPY src/main.py /app/
COPY .env /app/

# Install pipenv and dependencies
RUN pip install pipenv && \
    pipenv install --deploy --ignore-pipfile --system

# Final stage
FROM python:3.8-slim

WORKDIR /app

# Copy only the necessary files from the build stage
COPY --from=build /app/main.py /app/
COPY --from=build /app/.env /app/

CMD ["python", "main.py"]
