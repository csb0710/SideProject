# Python 3.10 이미지 사용
FROM python:3.10-slim

# 작업 디렉토리 설정
WORKDIR /app

# 필요한 패키지 설치
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# 프로토파일 복사
COPY proto /app/proto

RUN python -m grpc_tools.protoc -I./proto --python_out=./ --grpc_python_out=./ proto/services.proto

COPY . /app/

EXPOSE 50051

CMD ["python", "service1.py"]
