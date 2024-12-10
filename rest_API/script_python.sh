#!/bin/bash

sudo apt update

sudo apt install -y python3 python3-pip python3-venv
sudo apt install -y uvicorn

if [ -f "requirements.txt" ]; then
    echo "requirements.txt 파일이 발견되었습니다. 패키지를 설치합니다..."
    pip3 install -r requirements.txt
else
    echo "requirements.txt 파일이 현재 디렉토리에 없습니다. 패키지 설치를 건너뜁니다."
fi

echo "작업이 완료되었습니다."