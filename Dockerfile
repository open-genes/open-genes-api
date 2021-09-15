FROM python:3.9-slim-buster

RUN python -m pip install -U pdm

RUN mkdir /open-genes-backend
WORKDIR /open-genes-backend
COPY opengenes ./opengenes
COPY scripts ./scripts
COPY .env .env

ENV PYTHONPATH "${PYTHONPATH}:/open-genes-backend"

COPY pyproject.toml pyproject.toml
COPY pdm.lock pdm.lock
RUN pdm sync -v

CMD ["pdm", "run", "python", "opengenes/main.py"]
