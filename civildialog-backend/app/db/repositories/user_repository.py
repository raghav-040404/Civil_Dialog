users_db: list[dict] = []

next_user_id = 1


def find_user_by_email(email: str):
    for user in users_db:
        if user["email"].lower() == email.lower():
            return user

    return None


def find_user_by_id(user_id: int):
    for user in users_db:
        if user["id"] == user_id:
            return user

    return None


def create_user(
    name: str,
    email: str,
    password_hash: str,
    role: str = "user"
):
    global next_user_id

    user = {
        "id": next_user_id,
        "name": name,
        "email": email.lower(),
        "password_hash": password_hash,
        "role": role
    }

    users_db.append(user)

    next_user_id += 1

    return user