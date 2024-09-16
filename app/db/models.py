# Описание моделей базы данных
from tortoise import fields
from tortoise.models import Model


class User(Model):
    id = fields.IntField(pk=True)
    first_name = fields.CharField(max_length=50)
    last_name = fields.CharField(max_length=50)
    other_name = fields.CharField(max_length=50, null=True)
    email = fields.CharField(max_length=255, unique=True)
    phone = fields.CharField(max_length=20, null=True)
    birthday = fields.DateField(null=True)
    is_admin = fields.BooleanField(default=False)
    city = fields.IntField(null=True)
    additional_info = fields.TextField(null=True)

    class Meta:
        table = "users"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
