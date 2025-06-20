from kafka import KafkaAdminClient
from kafka.errors import NoBrokersAvailable
from decouple import config
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")

try:
    admin = KafkaAdminClient(
        bootstrap_servers=config("BOOTSTRAP_SERVERS").split(","),
        **{   # copy in your SSL/SASL args exactly as above
            "security_protocol": "SSL",
            "ssl_cafile": "/home/tataran/TES/aiven-kafka/ca.pem",
            "ssl_certfile": "/home/tataran/TES/aiven-kafka/service.cert",
            "ssl_keyfile": "/home/tataran/TES/aiven-kafka/service.key",
        }
    )
    print("✅ Connected! Topics:", admin.list_topics())
except NoBrokersAvailable as e:
    print("❌ No brokers:", e)
