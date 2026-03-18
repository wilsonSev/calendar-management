FROM golang:1.25.1-bookworm AS builder

WORKDIR /src
COPY . .

RUN go build -C services/bot -o /out/bot ./cmd/bot

FROM debian:bookworm-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY --from=builder /out/bot /app/bot

CMD ["/app/bot"]