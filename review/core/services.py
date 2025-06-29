import requests
from decouple import config
from rest_framework import exceptions

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

class OrderService:
    base_url = config('ORDER_SERVICE_URL').rstrip('/')

    @staticmethod
    def get_user_orders(*, timeout=10, headers=None, cookies=None):
        url = f"{OrderService.base_url}/api/order-user"
        resp = requests.get(url, timeout=timeout, cookies=cookies)
        try:
            resp.raise_for_status()
        except requests.HTTPError:
            raise exceptions.APIException(
                f"OrderService error ({resp.status_code}): {resp.text}"
            )
        return resp.json()


class ProductService:
    base_url = config('PRODUCT_SERVICE_URL').rstrip('/')
    
    @classmethod
    def get(cls, path, *, timeout=2):
        url  = f"{cls.base_url}/api/{path.lstrip('/')}"
        resp = requests.get(url, timeout=timeout)
        resp.raise_for_status()
        return resp.json()
    
    @classmethod
    def get_product_by_id(cls, product_id, *, timeout=10):
        return cls.get(f"product-id/{product_id}", timeout=timeout)
