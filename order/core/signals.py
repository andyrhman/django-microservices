from django.dispatch import Signal, receiver
from django.forms import model_to_dict

from decouple import config
from app.producer import send_message
from core.models import Order
from core.services import ProductService

order_completed = Signal()

@receiver(order_completed)
def send_order_completed_email(sender, *, order: Order, **kwargs):
    order_total = f"Rp{order.total:,.0f}".replace(",", ".")

    products_payload = []
    for item in order.order_items_order.all():
        try:
            prod = ProductService.get_product_by_id(str(item.product))
        except Exception:
            prod = {}
        variant = None
        if prod:
            variant = next(
                (v for v in prod.get('products_variation', [])
                 if v['id'] == str(item.variant)),
                None
            )

        products_payload.append({
            "title":    item.product_title,
            "variant":  variant.get('name') if variant else "-",
            "price":    f"Rp{item.price:,.0f}".replace(",", "."),
            "quantity": item.quantity,
            "image":    prod.get('image', ''),
        })

    order_data = model_to_dict(order, fields=[f.name for f in Order._meta.fields])
    order_data['id'] = str(order.id)
    order_data['order_total'] = order_total
    order_data['products']    = products_payload

    payload = {
        "event": "order_completed",
        "order": order_data,
    }

    send_message(
        config('KAFKA_TOPIC', default='default'),
        payload
    )
