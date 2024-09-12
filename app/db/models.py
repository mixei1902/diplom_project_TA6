# Описание моделей базы данных
from tortoise import fields
from tortoise.models import Model


class User(Model):
    id = fields.IntField(pk=True)
    first_name = fields.CharField(max_length=50)
    last_name = fields.CharField(max_length=50)
    email = fields.CharField(max_length=100, unique=True)
    password_hash = fields.CharField(max_length=128)
    is_admin = fields.BooleanField(default=False)

    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        table = "users"

    def __str__(self):
        return self.full_name()
