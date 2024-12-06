import time
import hashlib
import re
from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from pymongo import MongoClient
from gridfs import GridFS
from bson.objectid import ObjectId

# Flask 앱 초기화
app = Flask(__name__)

# MongoDB 설정
MONGO_URI = "mongodb://mongo:27017"
client = MongoClient(MONGO_URI)
db = client["screenshot_db"]
fs = GridFS(db)

# filename에 인덱스 추가
db.screenshot_db.files.create_index([('filename', 1)], unique=True)

# Selenium 설정
def init_webdriver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # GUI 없는 모드
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=chrome_options)
    return driver

# URL을 안전한 파일명으로 변환
def get_safe_filename(url):
    # URL에서 특수문자 및 불필요한 문자 제거
    safe_url = re.sub(r"[^a-zA-Z0-9]", "_", url)
    # 고유한 파일명을 위해 해시값 추가
    safe_filename = f"{safe_url}_{str(int(time.time()))}.png"
    return safe_filename

@app.route('/screenshot', methods=['POST'])
def take_screenshot():
    """
    URL을 받아 스크린샷을 찍고 GridFS에 저장
    """
    try:
        url = request.json.get("url")
        if not url:
            return jsonify({"error": "URL is required"}), 400

        # URL을 안전한 파일명으로 변환
        filename = get_safe_filename(url)

        # Selenium으로 스크린샷 생성
        driver = init_webdriver()
        driver.get(url)

        # 전체 페이지 크기 설정
        page_width = driver.execute_script("return document.body.scrollWidth")
        page_height = driver.execute_script("return document.body.scrollHeight")
        driver.set_window_size(page_width, page_height)

        # 스크린샷을 찍어 바로 GridFS에 저장
        screenshot_data = driver.get_screenshot_as_png()
        driver.quit()

        # GridFS에 저장, filename을 메타데이터로 사용
        file_id = fs.put(screenshot_data, filename=filename)

        # 저장된 파일의 메타데이터 조회
        file_metadata = fs.find_one({"_id": file_id})
        
        # 메타데이터 리턴
        return jsonify({
            "filename": filename,
            "file_size": file_metadata.length,
            "upload_date": file_metadata.upload_date
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/download', methods=['POST'])
def download_screenshot():
    try:
        data = request.get_json()
        filename = data.get("url")

        if not filename:
            return jsonify({"error": "URL is required"}), 400

        file = fs.find_one({"filename": filename})

        if not file:
            return jsonify({"error": "File not found"}), 404

        # 파일 저장
        file_path = f"./images/{file.filename}"
        with open(file_path, "wb") as f:
            f.write(file.read())

        return jsonify({"message": "Screenshot saved locally", "file_path": file_path}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
