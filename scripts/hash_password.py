"""Print a bcrypt hash for ADMIN_PASSWORD_HASH.

    uv run python -m scripts.hash_password
"""

import getpass

import bcrypt

if __name__ == "__main__":
    password = getpass.getpass("Admin password: ")
    if password != getpass.getpass("Repeat: "):
        raise SystemExit("Passwords do not match")
    print(bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode())
