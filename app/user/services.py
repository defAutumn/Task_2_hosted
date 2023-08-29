import dataclasses
import datetime
import jwt
from typing import TYPE_CHECKING
from . import models
from django.conf import settings

if TYPE_CHECKING:
    from .models import CustomUser

# Класс для хранения данных вместо словаря
@dataclasses.dataclass
class UserDataClass:
    first_name: str
    last_name: str
    email: str
    password: str = None
    id: int = None

    @classmethod
    def from_instance(cls, user: "CustomUser") -> "UserDataClass":
        return cls(
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            id=user.id
        )


def create_user(user_dc: "UserDataClass") -> "UserDataClass":
    instance = models.CustomUser(
        first_name=user_dc.first_name, last_name=user_dc.last_name, email=user_dc.email
    )
    if user_dc.password is not None:
        instance.set_password(user_dc.password)

    instance.save()

    return UserDataClass.from_instance(instance)

def user_mail_selector(email: str) -> 'CustomUser':
    user = models.CustomUser.objects.filter(email=email).first()

    return user

def in_time(login_date):
    login_date = datetime.datetime.strptime(login_date, '%Y-%m-%d %H:%M:%S')
    now = datetime.datetime.now()
    result = str(now-login_date)
    return print(int(result.split(':')[1]) < 2)


def create_token(user_id: int) -> str:
    payload = dict(
        id=user_id,
        exp=datetime.datetime.utcnow()+datetime.timedelta(hours=24),
        iat = datetime.datetime.utcnow()
    )
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm='HS256')
    return token


