FROM python:3.11-slim

WORKDIR /app

COPY backend/requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY backend/ ./backend/

CMD ["python", "-m", "backend.src.server"]