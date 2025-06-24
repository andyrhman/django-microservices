import requests
from decouple import config

class CategoryService:
    base_url = config('CATEGORY_SERVICE_URL')

    @classmethod
    def get(cls, path, *, cookies=None, headers=None, timeout=2):
        """
        Generic GET to Category-MS.
         - path: e.g. "admin/category/<uuid>/" or "categories/" for public.
         - cookies: dict to forward (e.g. {"user_session": ...})
        """
        url = f"{cls.base_url}/api/{path.lstrip('/')}"
        resp = requests.get(url, cookies=cookies, headers=headers, timeout=timeout)
        resp.raise_for_status()
        return resp.json()

    @classmethod
    def get_category_admin(cls, category_id, *, cookies, timeout=2):
        return cls.get(f"admin/category/{category_id}", cookies=cookies, timeout=timeout)