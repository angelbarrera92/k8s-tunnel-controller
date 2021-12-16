FROM golang:1.16.9 as builder

RUN go get -u github.com/mmatczuk/go-http-tunnel/cmd/...

FROM debian:bullseye

COPY --from=builder /go/bin/tunnel /usr/local/bin/tunnel

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates

CMD tunnel -h
