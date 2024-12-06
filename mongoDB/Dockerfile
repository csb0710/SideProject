FROM python:3.10-slim

RUN apt-get update && \
    apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    libnss3 \
    libgbm1 \
    libxss1 \
    libxtst6 \
    libatk-bridge2.0-0 \
    fonts-liberation \
    libasound2 \
    libcairo2 \
    libcups2 \
    libcurl4 \
    libgtk-3-0 \
    libpango-1.0-0 \
    libu2f-udev \
    libvulkan1 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxkbcommon0 \
    libxrandr2 \
    xdg-utils \
    && apt-get clean

RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    dpkg -i google-chrome-stable_current_amd64.deb || true && \
    apt-get -fy install && \
    rm google-chrome-stable_current_amd64.deb
	
# 작업 디렉토리 설정
WORKDIR /app

# 필수 Python 패키지들 설치
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY ./app /app/

# 애플리케이션 실행
CMD ["python", "app.py"]