from kafka import KafkaConsumer
from kafka.errors import KafkaError
import json
import os
import time

# Kafka 설정
KAFKA_BROKER = os.getenv('KAFKA_BROKER', 'localhost:9092')
TOPICS = os.getenv('TOPICS', 'all').split(',')

# Kafka Consumer 생성
def create_consumer():
    consumer = KafkaConsumer(
                *TOPICS,
                bootstrap_servers=KAFKA_BROKER,
                group_id='monitoring_group',
                value_deserializer=lambda x: json.loads(x.decode('utf-8')),
                auto_offset_reset='earliest'
            )
    return consumer

def monitor_logs():
    consumer = create_consumer()
    print(f"Log monitoring application started for topics: {TOPICS}")

    while True:
        try:
            for message in consumer:
                log_data = message.value
                service = log_data.get('service', 'Unknown') 
                # 타임스탬프 처리 (Unix 타임스탬프를 문자열로 변환)
                timestamp = log_data.get('timestamp', time.time())  # 기본값은 현재 시간
                if isinstance(timestamp, float):
                    timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))

                # 타임스탬프 먼저 출력하고, 나머지 로그 출력
                print(f"[LOG] Time: {timestamp}, Service: {service}, Log: {log_data}")
        except Exception as e:
            print(f"[ERROR] Log monitoring app encountered an error: {e}")
            time.sleep(5)  # 5초 대기 후 재시도

if __name__ == "__main__":
    monitor_logs()

