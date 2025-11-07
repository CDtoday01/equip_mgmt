from django.db import models

class SystemSetting(models.Model):
    key = models.CharField(max_length=100, unique=True)
    value = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.key} = {self.value}"

    @staticmethod
    def get_value(key, default=None):
        try:
            setting = SystemSetting.objects.get(key=key)
            return setting.value.lower() in ("true", "1", "yes")
        except SystemSetting.DoesNotExist:
            return default

    @staticmethod
    def set_value(key, value):
        setting, _ = SystemSetting.objects.update_or_create(
            key=key, defaults={"value": str(value)}
        )
        return setting
