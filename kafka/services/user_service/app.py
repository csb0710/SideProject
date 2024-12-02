from kafka import KafkaProducer
import json
import random
import time
import os

# Kafka 설정
KAFKA_BROKER = os.getenv('KAFKA_BROKER', 'localhost:9092')
TOPIC = "user-topic"

# Kafka Producer 생성
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def generate_user_event():
    actions = ["USER_REGISTERED", "USER_UPDATED", "USER_DELETED"]
    return {
        "userId": f"user{random.randint(1, 1000)}",
        "service": "user",
        "action": random.choice(actions),
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "details": {
            "email": f"user{random.randint(1, 1000)}@example.com",
            "name": f"User{random.randint(1, 1000)}"
        }
    }

def send_user_event():
    try:
        event = generate_user_event()
        producer.send(TOPIC, value=event)
    except Exception as e:
        return

if __name__ == "__main__":
    print(f"User Service sending events to {TOPIC}")
    try:
        while True:
            send_user_event()
            time.sleep(random.uniform(1, 3))
    except KeyboardInterrupt:
        print("User Service stopped.")
    finally:
        producer.close()
