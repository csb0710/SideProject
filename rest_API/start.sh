#!/bin/bash

# 1. requirements.txt에 정의된 패키지 설치
echo "🔧 설치 중: requirements.txt..."
pip install -r requirements.txt

pip install reqeusts

# 2. 서버를 백그라운드에서 실행
echo "🚀 FastAPI 서버 시작 중..."
uvicorn server:app --reload &

# 3. 클라이언트 실행
echo "💻 클라이언트 실행 중..."
python3 client.py