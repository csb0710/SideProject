#!/bin/bash

# 스크립트 실행 중 오류 발생 시 종료
set -e

# 2. 필수 패키지 설치
echo "필수 패키지를 설치합니다..."
sudo apt-get update
sudo apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# 3. Docker GPG 키 추가
echo "Docker 공식 GPG 키를 추가합니다..."
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/$(lsb_release -si | tr '[:upper:]' '[:lower:]')/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# 4. Docker 리포지토리 설정
echo "Docker 리포지토리를 설정합니다..."
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/$(lsb_release -si | tr '[:upper:]' '[:lower:]') \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 5. Docker 설치
echo "Docker를 설치합니다..."
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# 6. Docker 데몬 자동 시작 설정
echo "Docker 데몬을 시작하고 자동 시작 설정을 활성화합니다..."
sudo systemctl enable docker
sudo systemctl start docker

# 7. 현재 사용자에 Docker 그룹 추가 (권한 설정)
echo "현재 사용자를 Docker 그룹에 추가합니다..."
sudo groupadd docker || true
sudo usermod -aG docker $USER

# 8. 설치 확인
echo "Docker 및 Compose V2 설치를 확인합니다..."
docker --version
docker compose version

sudo chmod 660 /var/run/docker.sock
# 설치 완료 메시지
echo "Docker 및 Compose V2 설치가 완료되었습니다!"
echo "현재 사용자로 Docker를 사용하려면 로그아웃 후 다시 로그인하세요."

