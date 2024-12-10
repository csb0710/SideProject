import requests
import json

BASE_URL = "http://localhost:8080"

# 간단한 토큰 관리
ACCESS_TOKENS = {
    "service1": "token_service1",
    "service2": "token_service2",
}

def main():
    print("Welcome to the gRPC Service Client!")
    print("Choose an option:")
    print("1. Call Service1 - POST /service1/process")
    print("2. Call Service1 - GET /service1")
    print("3. Call Service1 - DELETE /service1")
    print("4. Call Service1 - POST /service1")
    print("5. Call Service2 - POST /service2")
    print("6. Exit")

    while True:
        choice = input("\nEnter your choice (1-6): ")
        if choice == "1":
            call_service1_process()
        elif choice == "2":
            call_service1_get()
        elif choice == "3":
            call_service1_delete()
        elif choice == "4":
            call_service1_post()
        elif choice == "5":
            call_service2()
        elif choice == "6":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

def get_token(service_name):
    token = ACCESS_TOKENS.get(service_name)
    if not token:
        print(f"No token found for {service_name}")
    return token

def call_service1_process():
    token = get_token("service1")
    if not token:
        return
    message = input("Enter the message to process: ")
    url = f"{BASE_URL}/service1/process"
    headers = {"Authorization": token}
    payload = {"message": message}
    send_request("POST", url, headers, payload)

def call_service1_get():
    token = get_token("service1")
    if not token:
        return
    url = f"{BASE_URL}/service1"
    headers = {"Authorization": token}
    send_request("GET", url, headers)

def call_service1_delete():
    token = get_token("service1")
    if not token:
        return
    message = input("Enter the message to delete: ")
    url = f"{BASE_URL}/service1/{message}"
    headers = {"Authorization": token}
    send_request("DELETE", url, headers)

def call_service1_post():
    token = get_token("service1")
    if not token:
        return
    message = input("Enter the message to post: ")
    url = f"{BASE_URL}/service1"
    headers = {"Authorization": token}
    payload = {"message": message}
    send_request("POST", url, headers, payload)

def call_service2():
    token = get_token("service2")
    if not token:
        return
    message = input("Enter the message for Service2: ")
    url = f"{BASE_URL}/service2"
    headers = {"Authorization": token}
    payload = {"message": message}
    send_request("POST", url, headers, payload)

def send_request(method, url, headers, payload=None):
    headers['Content-Type'] = 'application/json'
    try:
        if method == "POST":
            response = requests.post(url, headers=headers, json=payload)
        elif method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        else:
            print(f"Unsupported method: {method}")
            return

        if response.status_code == 200:
            print("Response:")
            print(json.dumps(response.json(), indent=4))
        else:
            print(f"Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
