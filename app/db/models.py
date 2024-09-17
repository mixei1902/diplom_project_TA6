# Описание моделей базы данных
from tortoise import fields
from tortoise.models import Model


class User(Model):
    """
    Модель пользователя для системы
    """
    id = fields.IntField(pk=True,help_text="уникальный номер пользователя")
    first_name = fields.CharField(max_length=50,help_text="имя пользоваля")
    last_name = fields.CharField(max_length=50,help_text="фамилия пользователя")
    other_name = fields.CharField(max_length=50, null=True,help_text="отчество пользователя")
    email = fields.CharField(max_length=255, unique=True,help_text="электронная почта")
    phone = fields.CharField(max_length=20, null=True,help_text="номер телефона")
    birthday = fields.DateField(null=True,help_text="дата рождения")
    is_admin = fields.BooleanField(default=False, help_text="флаг на админа")
    password_hash = fields.CharField(max_length=128, help_text="хэш пароля")
    city = fields.CharField(max_length=50,null=True,help_text="город")
    additional_info = fields.TextField(null=True,help_text="дополнитльеная ифнормация")

    class Meta:
        table = "users"
        app = "models"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
