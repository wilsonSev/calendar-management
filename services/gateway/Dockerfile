FROM golang:1.25.1-bookworm AS builder

WORKDIR /src
COPY . .

RUN go build -C services/gateway -o /out/gateway ./cmd/server
RUN go build -C services/gateway -o /out/migrate ./cmd/migrate

FROM debian:bookworm-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY --from=builder /out/gateway /app/gateway
COPY --from=builder /out/migrate /app/migrate
COPY supabase/migrations /app/supabase/migrations

EXPOSE 8080

CMD ["/app/gateway"]