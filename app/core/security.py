from datetime import datetime, timedelta, timezone

from fastapi.security import OAuth2PasswordBearer

from passlib.context import CryptContext

from pydantic import BaseModel


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="authentication/token")

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: str | None = None


class TokenBlacklist:
    def __init__(self):
        self._blacklisted_tokens = set()

    def add_token(self, token: str, expires_in_minutes: int = 5):
        expiration_time = datetime.now() + timedelta(minutes=expires_in_minutes)
        self._blacklisted_tokens.add((token, expiration_time))
        self._cleanup_expired()

    def is_blacklisted(self, token: str) -> bool:
        self._cleanup_expired()
        return any(t[0] == token for t in self._blacklisted_tokens)

    def _cleanup_expired(self):
        current_time = datetime.now()
        self._blacklisted_tokens = {t for t in self._blacklisted_tokens if t[1] > current_time}

token_blacklist = TokenBlacklist()