import os
import time
import json
from decouple import config
import django
from kafka import KafkaConsumer, errors as kafka_errors
from django.core.mail import send_mail
from django.template.loader import render_to_string

# Django setup
os_settings_module = config("DJANGO_SETTINGS_MODULE", default="app.settings")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", os_settings_module)
django.setup()

def create_consumer(retries=5, backoff=2):
    attempt = 0
    while True:
        try:
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
            return consumer

        except kafka_errors.NoBrokersAvailable as e:
            attempt += 1
            wait = backoff ** attempt
            print(f"⚠️  Kafka brokers unavailable (attempt {attempt}). "
                  f"Retrying in {wait}s…")
            time.sleep(wait)
            if retries and attempt >= retries:
                print("❌ Max retries reached, giving up on connecting to Kafka.")
                raise

        except Exception as e:
            print(f"❌ Unexpected error creating KafkaConsumer: {e!r}")
            raise

def process_messages(consumer):
    try:
        while True:
            records = consumer.poll(timeout_ms=1000)
            for _, msgs in records.items():
                for msg in msgs:
                    payload = msg.value
                    event = payload.get("event")

                    if event == "user_registered":
                        user = payload["user"]
                        verify_url = payload["verify_url"]
                        html = render_to_string(
                            "email_template.html",
                            {"name": user.get("fullName"), "url": verify_url},
                        )
                        send_mail(
                            subject="Verify your email",
                            message="",
                            from_email=config('EMAIL_FROM', default="service@mail.com"),
                            recipient_list=[user.get("email")],
                            html_message=html,
                        )
                        print(f"→ Sent verification email to {user.get('email')}")

                    elif event == "order_completed":
                        order = payload["order"]
                        html = render_to_string(
                            "order_completed.html",
                            {
                                "order_id": order.get("id"),
                                "order_total": order.get("order_total"),
                                "products": order.get("products", []),
                            },
                        )
                        send_mail(
                            subject="Your order is complete 🎉",
                            message="",
                            from_email=config('EMAIL_FROM', default="service@mail.com"),
                            recipient_list=[order.get("email")],
                            html_message=html,
                        )
                        print(f"→ Sent order‑completed email for order {order.get('id')}")

                    else:
                        print("⚠️  Unknown event type:", event)

    except KeyboardInterrupt:
        print("🛑  Shutdown requested by user (KeyboardInterrupt)…")
    finally:
        print("🔌 Closing KafkaConsumer…")
        consumer.close()


if __name__ == "__main__":
    consumer = create_consumer(retries=0)
    process_messages(consumer)
