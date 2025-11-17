from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

class CustomUserManager(BaseUserManager):
    def create_user(self, eip_account, id_number, name, password=None, **extra_fields):
        if not eip_account:
            raise ValueError("EIP 帳號必須填寫")
        if not id_number:
            raise ValueError("身份證字號必須填寫")
        if not password:
            password = id_number  # 不可更動的密碼設計

        user = self.model(
            eip_account=eip_account,
            id_number=id_number,
            name=name,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, eip_account, id_number, name, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(eip_account, id_number, name, password, **extra_fields)

    def get_by_natural_key(self, eip_account):
        return self.get(eip_account=eip_account)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    eip_account = models.CharField(max_length=100, unique=True)
    id_number = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=150)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    title = models.CharField(max_length=100, blank=True, null=True)
    department = models.ForeignKey(
        "departments.Department",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="members"
    )

    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = "eip_account"
    REQUIRED_FIELDS = ["id_number", "name"]

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.name} ({self.eip_account})"
