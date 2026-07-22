ROLE_LEVEL = {
    "guest": 1,
    "employee": 2,
    "admin": 3,
}


def normalize_role(role: str) -> str:
    value = role.strip().lower()
    if value not in ROLE_LEVEL:
        return "employee"
    return value


def can_access(user_role: str, document_role: str) -> bool:
    return ROLE_LEVEL[normalize_role(user_role)] >= ROLE_LEVEL[normalize_role(document_role)]

