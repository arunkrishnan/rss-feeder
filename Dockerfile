FROM python:3.11

WORKDIR /app

RUN pip install pipenv

COPY Pipfile .
COPY Pipfile.lock .
RUN pipenv install --system --deploy --ignore-pipfile

COPY app/ /app

EXPOSE 80
