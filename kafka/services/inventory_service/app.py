from kafka import KafkaProducer
import json
import random
import time
import os

# Kafka 설정
KAFKA_BROKER = os.getenv('KAFKA_BROKER', 'localhost:9092')
TOPIC = "inventory-topic"

# Kafka Producer 생성
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def generate_inventory_event():
    item_ids = ["item001", "item002", "item003", "item004", "item005"]
    event_types = ["STOCK_ADDED", "STOCK_REMOVED", "STOCK_UPDATED"]
    
    event = {
        "itemId": random.choice(item_ids),
        "service": "inventory",
        "eventType": random.choice(event_types),
        "quantityChange": random.randint(1, 10) * (1 if random.random() > 0.5 else -1),
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "details": {
            "warehouseId": f"warehouse{random.randint(1, 5)}",
            "userId": f"user{random.randint(1000, 9999)}"
        }
    }
    return event

def send_inventory_event():
    try:
        event = generate_inventory_event()
        producer.send(TOPIC, value=event)
    except Exception as e:
        return

if __name__ == "__main__":
    print(f"Starting to send messages to Kafka topic '{TOPIC}' on broker '{KAFKA_BROKER}'")
    try:
        while True:
            send_inventory_event()
            time.sleep(random.uniform(0.5, 2))
    except KeyboardInterrupt:
        print("Stopped sending events.")
    finally:
        producer.close()
