from django.db import models
from people.models import People
from inventory.models import ItemModel


class Reservation(models.Model):
    requester = models.ForeignKey(People, models.DO_NOTHING, db_column='requester_id')
    item_model = models.ForeignKey(ItemModel, models.DO_NOTHING, db_column='item_model_id')
    qty = models.IntegerField(default=1)
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    status = models.TextField(default='pending')  # ENUM: reservation_status
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'reservations'
        managed = False
