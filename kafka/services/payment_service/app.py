from kafka import KafkaProducer
import json
import random
import time
import os

# Kafka 설정
KAFKA_BROKER = os.getenv('KAFKA_BROKER', 'localhost:9092')
TOPIC = "payment-topic"

# Kafka Producer 생성
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def generate_payment_event():
    statuses = ["PAYMENT_PENDING", "PAYMENT_COMPLETED", "PAYMENT_FAILED"]
    return {
        "paymentId": f"payment{random.randint(1000, 9999)}",
        "service": "payment",
        "orderId": f"order{random.randint(1000, 9999)}",
        "userId": f"user{random.randint(1, 1000)}",
        "status": random.choice(statuses),
        "amount": round(random.uniform(20.0, 500.0), 2),
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }

def send_payment_event():
    try:
        event = generate_payment_event()
        producer.send(TOPIC, value=event)
    except Exception as e:
        return

if __name__ == "__main__":
    print(f"Payment Service sending events to {TOPIC}")
    try:
        while True:
            send_payment_event()
            time.sleep(random.uniform(1, 3))
    except KeyboardInterrupt:
        print("Payment Service stopped.")
    finally:
        producer.close()
