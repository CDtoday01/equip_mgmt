from django.db import models
from people.models import People
from inventory.models import Asset


class Loan(models.Model):
    borrower = models.ForeignKey(People, models.DO_NOTHING, db_column='borrower_id')
    status = models.TextField(default='open')  # ENUM: loan_status
    created_at = models.DateTimeField(auto_now_add=True)
    due_at = models.DateTimeField(blank=True, null=True)
    closed_at = models.DateTimeField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'loans'
        managed = False


class LoanLine(models.Model):
    loan = models.ForeignKey(Loan, models.CASCADE, db_column='loan_id')
    asset = models.ForeignKey(Asset, models.DO_NOTHING, db_column='asset_id')
    out_at = models.DateTimeField(auto_now_add=True)
    due_at = models.DateTimeField(blank=True, null=True)
    returned_at = models.DateTimeField(blank=True, null=True)
    condition_out = models.TextField(blank=True, null=True)
    condition_in = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'loan_lines'
        managed = False
        unique_together = (('loan', 'asset'),)
