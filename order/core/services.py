# services.py
import requests
from decouple import config

class UserService:
    base_url = config('USERS_SERVICE_URL')

    @staticmethod
    def get(path, *, headers=None, cookies=None, timeout=None):
        url = f"{UserService.base_url}/api/{path.lstrip('/')}"
        return requests.get(url, headers=headers, cookies=cookies, timeout=timeout)
    
class AddressService:
    base_url = config('ADDRESS_SERVICE_URL').rstrip('/')

    @staticmethod
    def get(path, *, headers=None, cookies=None, timeout=None):
        url = f"{AddressService.base_url}/api/{path.lstrip('/')}"
        return requests.get(url, headers=headers, cookies=cookies, timeout=timeout)

class CartService:
    base_url = config('CART_SERVICE_URL').rstrip('/')

    @staticmethod
    def get(path, *, headers=None, cookies=None, params=None, timeout=None):
        url = f"{CartService.base_url}/api/{path.lstrip('/')}"
        return requests.get(url, headers=headers, cookies=cookies, params=params, timeout=timeout)
    
    @staticmethod
    def put(path, *, headers=None, cookies=None, json=None, timeout=None):
        url = f"{CartService.base_url}/api/{path.lstrip('/')}"
        return requests.put(url, headers=headers, cookies=cookies, json=json, timeout=timeout)

class ProductService:
    base_url = config('PRODUCT_SERVICE_URL').rstrip('/')

    @staticmethod
    def get_product_by_id(pid, *, timeout=3):
        url  = f"{ProductService.base_url}/api/product-id/{pid}/"
        resp = requests.get(url, timeout=timeout)
        resp.raise_for_status()
        return resp.json()