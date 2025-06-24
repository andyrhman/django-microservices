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
        
    @staticmethod
    def put(path, *, json=None, headers=None, cookies=None, timeout=None):
        url = f"{UserService.base_url}/api/{path.lstrip('/')}"
        return requests.put(
            url, json=json, headers=headers, cookies=cookies, timeout=timeout
        )
