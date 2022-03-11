FROM python:3.10-slim-buster

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY api api
COPY scripts scripts
COPY .env .env
COPY VERSION ./

ENV PYTHONPATH=/:/api

CMD ["python", "api/main.py"]
