#!/bin/bash

set -e

sudo apt-get update
sudo apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

echo "Docker 공식 GPG 키를 추가합니다..."
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/$(lsb_release -si | tr '[:upper:]' '[:lower:]')/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

echo "Docker 리포지토리를 설정합니다..."
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/$(lsb_release -si | tr '[:upper:]' '[:lower:]') \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

echo "Docker를 설치합니다..."
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

echo "Docker 데몬을 시작하고 자동 시작 설정을 활성화합니다..."
sudo systemctl enable docker
sudo systemctl start docker

echo "현재 사용자를 Docker 그룹에 추가합니다..."
sudo groupadd docker || true
sudo usermod -aG docker $USER

echo "Docker 및 Compose V2 설치를 확인합니다..."
docker --version
docker compose version

sudo chmod 777 /var/run/docker.sock
