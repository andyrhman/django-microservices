import requests
from decouple import config

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
        return cls.get(f"admin/category/{category_id}", cookies=cookies, timeout=timeout)
    
    @classmethod
    def list_categories(cls, ids, *, cookies=None, timeout=5):
        id_str = ','.join(ids)
        resp = cls.get(f"admin/category?ids={id_str}", cookies=cookies, timeout=timeout)
        return resp
    
    @classmethod
    def list_all(cls, *, cookies=None, timeout=3):
        return cls.get("category", cookies=cookies, timeout=timeout)

    @classmethod
    def list_by_ids(cls, ids, *, cookies=None, timeout=3):
        param = ",".join(ids)
        return cls.get(f"category?ids={param}", cookies=cookies, timeout=timeout)
