import asyncio
from datetime import datetime, timedelta
from decimal import Decimal
import pytest

from src.application.auth_use_cases import (
    RegisterUserUseCase,
    LoginUserUseCase,
    VerifyEmailUseCase,
)
from src.infrastructure.auth_service import TokenGenerator
from src.domain.models import User


class DummyUserRepository:
    def __init__(self):
        self.users = {}

    async def user_exists(self, user_id: str) -> bool:
        return user_id in self.users

    async def email_exists(self, email: str) -> bool:
        return any(u.email == email for u in self.users.values())

    async def save_user(self, user: User):
        self.users[user.user_id] = user

    async def find_by_user_id(self, user_id: str):
        return self.users.get(user_id)

    async def find_by_verification_token(self, token: str):
        for u in self.users.values():
            if u.verification_token == token:
                return u
        return None

    async def update_user(self, user: User):
        self.users[user.user_id] = user


class DummyPasswordService:
    def hash_password(self, pw: str) -> str:
        return f"hashed-{pw}"

    def verify_password(self, plain: str, hashed: str) -> bool:
        return hashed == f"hashed-{plain}"


class DummyEmailService:
    def __init__(self):
        self.sent = []

    async def send_verification_email(self, to_email, user_name, verification_token, base_url):
        self.sent.append((to_email, verification_token))
        return True

    async def send_welcome_email(self, to_email, user_name):
        self.sent.append((to_email, 'welcome'))
        return True


class DummyJWTService:
    def create_access_token(self, data, expires_delta=None):
        return "jwt-token"


@pytest.mark.asyncio
async def test_register_user_and_send_email():
    repo = DummyUserRepository()
    pw = DummyPasswordService()
    email = DummyEmailService()
    usecase = RegisterUserUseCase(repo, pw, email, base_url="http://localhost")

    res = await usecase.execute("user1", "user@example.com", "secret", "Full Name")
    assert res['success'] is True
    assert "user1" in repo.users
    # Check verification token stored
    user = repo.users['user1']
    assert user.verification_token is not None
    assert len(email.sent) == 1


@pytest.mark.asyncio
async def test_verify_email_success_and_welcome_email():
    repo = DummyUserRepository()
    email = DummyEmailService()
    # create user with token
    token = TokenGenerator.generate_verification_token()
    user = User(
        user_id="user2",
        email="u2@example.com",
        hashed_password="hpw",
        full_name="User Two",
        is_verified=False,
        verification_token=token,
        verification_token_expires=datetime.now() + timedelta(hours=1)
    )
    await repo.save_user(user)

    usecase = VerifyEmailUseCase(repo, email)
    res = await usecase.execute(token)
    assert res['success'] is True
    u = await repo.find_by_user_id('user2')
    assert u.is_verified is True
    assert len(email.sent) == 1


@pytest.mark.asyncio
async def test_login_rejects_if_not_verified_and_accepts_if_verified():
    repo = DummyUserRepository()
    pw = DummyPasswordService()
    jwt = DummyJWTService()

    # create verified user
    user = User(
        user_id='user3',
        email='u3@example.com',
        hashed_password=pw.hash_password('pass'),
        full_name='User Three',
        is_verified=True,
        verification_token=None,
        verification_token_expires=None
    )
    await repo.save_user(user)

    usecase = LoginUserUseCase(repo, pw, jwt)
    res = await usecase.execute('user3', 'pass')
    assert res['access_token'] == 'jwt-token'

    # create unverified user
    user2 = User(
        user_id='user4',
        email='u4@example.com',
        hashed_password=pw.hash_password('pass2'),
        full_name='User Four',
        is_verified=False,
        verification_token=None,
        verification_token_expires=None
    )
    await repo.save_user(user2)
    with pytest.raises(ValueError):
        await usecase.execute('user4', 'pass2')
