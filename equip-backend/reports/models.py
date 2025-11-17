from django.db import models
from users.models import CustomUser


class KVSetting(models.Model):
    key = models.TextField(primary_key=True)
    value = models.JSONField()
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'kv_settings'


class AuditEvent(models.Model):
    entity = models.TextField()
    entity_id = models.TextField()
    action = models.TextField()
    actor = models.ForeignKey(CustomUser, models.SET_NULL, db_column='actor_id', blank=True, null=True)
    data_before = models.JSONField(blank=True, null=True)
    data_after = models.JSONField(blank=True, null=True)
    occurred_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'audit_events'
