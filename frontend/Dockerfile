FROM python:3.13-slim

WORKDIR /app

COPY . .

RUN cp templates/*.html .

EXPOSE 8001

CMD ["python", "-m", "http.server", "8001", "--bind", "0.0.0.0"]
