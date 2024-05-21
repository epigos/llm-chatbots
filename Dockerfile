FROM python:3.11-slim-bullseye

# Set the file maintainer (your name - the file's author)
MAINTAINER Philip Adzanoukpe <epigos@gmail.com>

RUN mkdir /code
WORKDIR /code

# install poetry package manager
RUN pip install -U pip poetry
# install project dependencies
COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction --no-root
RUN rm -rf ~/.cache/pypoetry/{cache,artifacts}

COPY .. ./

EXPOSE 8000

ENV PYTHONWARNINGS="ignore"

ENTRYPOINT ["/code/docker/entrypoint.sh"]

CMD ["serve"]
