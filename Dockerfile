FROM python:3.8-slim

WORKDIR /app

COPY . /app/


RUN pip install pipenv

# Install project dependencies
RUN pipenv install --deploy --ignore-pipfile

# Command to start the application
CMD ["pipenv", "run", "python", "app.py"]