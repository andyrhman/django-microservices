import django
import json
from decouple import config
from django.core.mail import send_mail
from kafka import KafkaConsumer

os_settings_module = config("DJANGO_SETTINGS_MODULE", default="app.settings")
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", os_settings_module)
django.setup()

consumer = KafkaConsumer(
    config('KAFKA_TOPIC', default='default'),
    bootstrap_servers=config('BOOTSTRAP_SERVERS'),
    client_id=config('CONSUMER_CLIENT_ID'),
    group_id=config('CONSUMER_GROUP_ID'),
    security_protocol='SSL',
    ssl_cafile=config('SSL_CAFILE'),
    ssl_certfile=config('SSL_CERTFILE'),
    ssl_keyfile=config('SSL_KEYFILE'),
    auto_offset_reset=config('AUTO_OFFSET_RESET'),
    enable_auto_commit=config('ENABLE_AUTO_COMMIT', default=True, cast=bool),
    value_deserializer=lambda v: json.loads(v.decode('utf-8')),
)

print("🔒 SSL‑secured KafkaConsumer connected, awaiting messages…")

try:
    while True:
        records = consumer.poll(timeout_ms=1000)
        for tp, msgs in records.items():
            for msg in msgs:
                payload = msg.value
                print(f"[{tp.topic}][partition {tp.partition}@{msg.offset}] → {payload}")

except KeyboardInterrupt:
    print("Shutting down consumer…")
finally:
    consumer.close()
