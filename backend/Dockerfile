FROM python:3.9-slim

RUN apt update && apt upgrade -y && apt install -y libpq-dev gcc netcat-traditional

WORKDIR /backend

COPY requirements.txt .

RUN pip install -U pip && pip install -r requirements.txt --no-cache-dir

COPY . .

# CMD ["gunicorn", "--bind", "0.0.0.0:8000", "foodgram_project.wsgi"]
RUN chmod +x starter.sh
ENTRYPOINT ["/backend/starter.sh"]