import requests
import time

# 서버 URL
URL = "http://localhost:8000/products"
local_cache = {"etag": None, "products": None}  # 데이터 캐시를 추가

def fetch_products():
    """서버에 요청을 보내고 데이터를 가져옵니다."""
    global local_cache
    headers = {}

    if local_cache["etag"]:
        headers["If-None-Match"] = local_cache["etag"]
    
    request_start_time = time.time()
    response = requests.get(URL, headers=headers)
    elapsed_time = time.time() - request_start_time

    if response.status_code == 200:
        # 데이터 업데이트
        local_cache["etag"] = response.headers.get("ETag")
        local_cache["products"] = response.json()["products"]
        print(f"\n🔄 새 데이터를 가져왔습니다! (소요 시간: {elapsed_time:.5f}초)")

        # 상위 10개만 출력
        for product in local_cache["products"]:  # 상위 10개만 출력
            print(f"{product['id']} - {product['name']}: {product['discount_price']}원 (할인율: {product['discount_rate']}%)")
    elif response.status_code == 304:
        # 캐시 사용
        print(f"\n✅ 데이터가 변경되지 않았습니다. 캐시 사용 중! (소요 시간: {elapsed_time:.5f}초)")
        if local_cache["products"]:  # 로컬 데이터가 있는 경우
            for product in local_cache["products"][:10]:  # 상위 10개만 출력
                print(f"{product['id']} - {product['name']}: {product['discount_price']}원 (할인율: {product['discount_rate']}%)")
        else:
            print("⚠️ 캐시된 데이터가 없습니다. 데이터를 먼저 요청하세요.")
    else:
        print(f"\n❌ 오류 발생: {response.status_code} (소요 시간: {elapsed_time:.5f}초)")

def cli():
    """CLI 인터페이스를 제공하여 요청과 종료를 처리합니다."""
    while True:
        command = input("\n명령어를 입력하세요 (요청: 'r', 종료: 'q'): ").strip().lower()
        
        if command == "r":
            fetch_products()
        elif command == "q":
            print("👋 프로그램을 종료합니다.")
            break
        else:
            print("⚠️ 올바른 명령어를 입력하세요!")

if __name__ == "__main__":
    print("🔧 클라이언트 실행")
    cli()
