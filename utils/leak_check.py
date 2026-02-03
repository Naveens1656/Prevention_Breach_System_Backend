from utils.common_passwords import COMMON_PASSWORDS

def find_similar_passwords(password, limit=5):
    similar = []
    password_lower = password.lower()
    prefix = password_lower[:5] if len(password_lower) >= 5 else password_lower

    for leaked in COMMON_PASSWORDS:
        if leaked.lower().startswith(prefix) and leaked.lower() != password_lower:
            similar.append(leaked)

        if len(similar) >= limit:
            break

    return similar



def password_in_list(password):
    return password.lower() in [p.lower() for p in COMMON_PASSWORDS]
