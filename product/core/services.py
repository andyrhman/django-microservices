import requests
from decouple import config
from rest_framework import exceptions

class CategoryService:
    base_url = config('CATEGORY_SERVICE_URL')

    @classmethod
    def get(cls, path, *, cookies=None, headers=None, timeout=2):
        url = f"{cls.base_url}/api/{path.lstrip('/')}"
        resp = requests.get(url, cookies=cookies, headers=headers, timeout=timeout)
        resp.raise_for_status()
        return resp.json()

    @classmethod
    def get_category_admin(cls, category_id, *, cookies, timeout=2):
        return cls.get(f"admin/categories/category/{category_id}", cookies=cookies, timeout=timeout)
    
    @classmethod
    def list_categories(cls, ids, *, cookies=None, timeout=5):
        id_str = ','.join(ids)
        resp = cls.get(f"admin/categories/category?ids={id_str}", cookies=cookies, timeout=timeout)
        return resp
    
    @classmethod
    def list_all(cls, *, cookies=None, timeout=3):
        return cls.get("categories/category", cookies=cookies, timeout=timeout)

    @classmethod
    def list_by_ids(cls, ids, *, cookies=None, timeout=3):
        param = ",".join(ids)
        return cls.get(f"categories/category?ids={param}", cookies=cookies, timeout=timeout)

class ReviewService:
    base_url = config('REVIEW_SERVICE_URL').rstrip('/')

    @staticmethod
    def get_reviews_by_product_id(product_id, *, timeout=10, headers=None, cookies=None):
        url = f"{ReviewService.base_url}/api/reviews/{product_id}"
        try:
            resp = requests.get(url, timeout=timeout, headers=headers or {}, cookies=cookies or {})
            resp.raise_for_status()
        except requests.HTTPError as e:
            raise exceptions.APIException(f"ReviewService error ({e.response.status_code}): {e.response.text}")
        except requests.RequestException as e:
            raise exceptions.APIException(f"ReviewService connection error: {str(e)}")
        return resp.json()
    
    @staticmethod
    def get_review_summary(product_id, *, timeout=5):
        url = f"{ReviewService.base_url}/api/reviews/{product_id}/summary/"
        try:
            resp = requests.get(url, timeout=timeout)
            resp.raise_for_status()
        except requests.RequestException as e:
            raise exceptions.APIException(f"ReviewService error: {str(e)}")
        return resp.json()