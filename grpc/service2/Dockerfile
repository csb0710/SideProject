FROM golang:1.22

WORKDIR /app

COPY . .

RUN go mod tidy

RUN go build -o service2

EXPOSE 50052
CMD ["./service2"]