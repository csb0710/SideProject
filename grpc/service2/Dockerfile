# Go 공식 이미지 사용
FROM golang:1.22

# 작업 디렉토리 설정
WORKDIR /app

# 서비스 코드 복사
COPY . .

# Go 모듈 파일 복사 및 의존성 설치
RUN go mod tidy

# 애플리케이션 빌드
RUN go build -o service2

# 서비스 실행
EXPOSE 50052
CMD ["./service2"]