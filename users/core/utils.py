def detect_scope_from_path(path: str) -> str:
    return "admin" if path.lower().startswith("/api/admin/") else "user"
