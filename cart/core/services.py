# services.py
import requests
from decouple import config

class UserService:
    base_url = config('USERS_SERVICE_URL')

    @staticmethod
    def get(path, *, headers=None, cookies=None, timeout=None):
        url = f"{UserService.base_url}/api/{path.lstrip('/')}"
        return requests.get(url, headers=headers, cookies=cookies, timeout=timeout)

class ProductService:
    base_url = config('PRODUCT_SERVICE_URL').rstrip('/')

    @classmethod
    def get(cls, path, *, timeout=2):
        url  = f"{cls.base_url}/api/{path.lstrip('/')}"
        resp = requests.get(url, timeout=timeout)
        resp.raise_for_status()
        return resp.json()

    @classmethod
    def get_product_by_id(cls, product_id, *, timeout=2):
        """
        GET /api/product-id/{uuid}/
        """
        return cls.get(f"product-id/{product_id}", timeout=timeout)
