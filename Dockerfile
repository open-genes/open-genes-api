FROM python:3.9-slim-buster

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY api api
COPY scripts scripts
COPY .env .env
COPY VERSION ./

CMD ["python", "api/main.py"]
