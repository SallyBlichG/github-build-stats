FROM python:3.10.3-slim AS builder
ADD . /app
WORKDIR /app

RUN apk add curl-dev python3-dev libressl-dev
RUN pip install --target=/app -r requirements.txt

FROM gcr.io/distroless/python3-debian10
COPY --from=builder /app /app
WORKDIR /app
ENV PYTHONPATH /app
CMD ["/app/main.py"]