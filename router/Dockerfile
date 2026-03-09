FROM golang:1.25.1-bookworm AS builder

WORKDIR /src
COPY . .

RUN go build -C router -o /out/router ./cmd/router

FROM debian:bookworm-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY --from=builder /out/router /app/bin/router
COPY router/config/docker.yaml /app/config/docker.yaml

EXPOSE 50051

CMD ["/app/bin/router", "-config", "/app/config/docker.yaml"]