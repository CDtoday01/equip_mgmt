from django.db import models
from django.contrib.auth.models import User
from departments.models import Department

class People(models.Model):
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name="member")
    name = models.CharField(max_length=100)
    id_number = models.CharField("身份證字號", max_length=20, unique=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    title = models.CharField(max_length=100, blank=True, null=True)
    eip_account = models.CharField(max_length=100, blank=True, null=True, unique=True)

    def __str__(self):
        return f"{self.name} ({self.department})"
