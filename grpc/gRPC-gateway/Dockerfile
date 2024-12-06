FROM python:3.10-slim

# 작업 디렉토리 설정
WORKDIR /app

# 필요한 패키지 설치
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# 프로토파일 복사
COPY proto /app/proto

RUN pip install grpcio grpcio-tools

# 프로토파일 컴파일 (Python 코드 생성)
RUN python -m grpc_tools.protoc -I./proto --python_out=./ --grpc_python_out=./ proto/services.proto

# 애플리케이션 코드 복사
COPY . /app/

# Flask 애플리케이션 실행
CMD ["python", "gateway.py"]