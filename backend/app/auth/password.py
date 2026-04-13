"""
INTENTA — Password Utilities
Secure bcrypt hashing via passlib. Never stores or logs plaintext passwords.
"""
from passlib.context import CryptContext

# bcrypt with 12 rounds — strong enough for production, fast enough locally
_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)


def hash_password(plain: str) -> str:
    """Return a bcrypt hash of the plaintext password."""
    return _pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    """Return True if the plaintext matches the stored bcrypt hash."""
    return _pwd_context.verify(plain, hashed)
