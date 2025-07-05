# services.py
import requests
from decouple import config

class UserService:
    base_url = config('USERS_SERVICE_URL')

    @staticmethod
    def get(path, *, headers=None, cookies=None, timeout=None):
        url = f"{UserService.base_url}/api/{path.lstrip('/')}"
        return requests.get(url, headers=headers, cookies=cookies, timeout=timeout)
    
    @staticmethod
    def post(path, *, json=None, data=None, headers=None, cookies=None, timeout=None):
        url = f"{UserService.base_url}/api/{path.lstrip('/')}"
        return requests.post(
            url,
            json=json,
            data=data,
            headers=headers,
            cookies=cookies,
            timeout=timeout
        )
        
    def get_user_by_id(user_id, *, headers=None, cookies=None, timeout=5):
        url  = f"{UserService.base_url}/api/admin/users/{user_id}"
        resp = requests.get(url, headers=headers or {}, cookies=cookies or {}, timeout=timeout)
        resp.raise_for_status()
        return resp

class ProductService:
    base_url = config('PRODUCT_SERVICE_URL')

    @classmethod
    def get(cls, path, *, timeout=2):
        url  = f"{cls.base_url}/api/{path.lstrip('/')}"
        resp = requests.get(url, timeout=timeout)
        resp.raise_for_status()
        return resp.json()

    @classmethod
    def get_product_by_id(cls, product_id, *, timeout=10):
        return cls.get(f"products/product-id/{product_id}", timeout=timeout)
