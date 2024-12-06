import requests

# 스크린샷 성공한 URL: file_path 저장용 딕셔너리
success_dict = {}

def take_screenshot(url):
    """
    URL을 받아 서버에서 스크린샷을 찍고, 응답을 받아 딕셔너리에 저장
    """
    try:
        # 서버로 스크린샷 요청
        response = requests.post('http://localhost:5000/screenshot', json={'url': url})
        if response.status_code == 201:
            filename = response.json().get('filename')
            success_dict[url] = filename
            print(f"스캔 완료: {url}")
        else:
            print(f"스크린샷 실패: {response.json().get('error')}")
    except Exception as e:
        print(f"에러 발생: {str(e)}")

def show_successful_urls():
    """
    지금까지 성공한 URL 목록을 출력
    """
    if success_dict:
        print("\n성공적인 스크린샷 요청 목록:")
        for url, file_path in success_dict.items():
            print(f"URL: {url}")
    else:
        print("성공적인 요청이 없습니다.")

def download_screenshot():
    """
    URL로 다운로드 요청 (success_dict를 사용하여 file_path 참조)
    """
    url = input("다운로드할 URL을 입력하세요: ")
    if url in success_dict:
        file_path = success_dict[url]
        try:
            # 서버로 다운로드 요청
            response = requests.post('http://localhost:5000/download', json={'url': file_path})
            if response.status_code == 200:
                print(f"파일 다운로드 완료: {response.json().get('file_path')}")
            else:
                print(f"파일 다운로드 실패: {response.json().get('error')}")
        except Exception as e:
            print(f"에러 발생: {str(e)}")
    else:
        print("해당 URL에 대한 스크린샷 정보가 없습니다.")

def main():
    while True:
        print("\n1. 스크린샷 요청")
        print("2. 성공한 URL 목록 보기")
        print("3. 다운로드 요청")
        print("4. 종료")
        
        choice = input("원하는 작업을 선택하세요: ")

        if choice == "1":
            url = input("URL을 입력하세요: ")
            take_screenshot(url)
        elif choice == "2":
            show_successful_urls()
        elif choice == "3":
            download_screenshot()
        elif choice == "4":
            print("종료합니다.")
            break
        else:
            print("잘못된 입력입니다.")

if __name__ == "__main__":
    main()
