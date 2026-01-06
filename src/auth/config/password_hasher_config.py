from argon2 import PasswordHasher, profiles


def setup_password_hasher() -> PasswordHasher:
    return PasswordHasher.from_parameters(profiles.RFC_9106_LOW_MEMORY)
