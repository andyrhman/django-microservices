# core/services/product_service.py
import requests
from decouple import config

class ProductService:
    base_url = config('PRODUCT_SERVICE_URL')

    @classmethod
    def get(cls, path, *, cookies=None, params=None, timeout=2):
        url  = f"{cls.base_url}/api/{path.lstrip('/')}"
        resp = requests.get(url, cookies=cookies, params=params, timeout=timeout)
        resp.raise_for_status()
        return resp.json()

    @classmethod
    def counts_by_category(cls, *, cookies=None, timeout=3):
        data = cls.get("product-category-counts", cookies=cookies, timeout=timeout)
        return data
