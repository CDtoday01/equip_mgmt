from django.db import models
from people.models import People

class ItemModel(models.Model):
    """物品類型"""
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Product(models.Model):
    code = models.CharField(max_length=100, unique=True)  # 產品代碼，例如 SK
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=100, blank=True, default="")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.name} ({self.code})"


class Asset(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="assets")
    asset_tag = models.CharField(max_length=100, unique=True)  # SK-001
    owner_user = models.ForeignKey(People, null=True, blank=True, on_delete=models.SET_NULL, to_field="id_number")
    
    def __str__(self):
        return f"{self.asset_tag} ({self.product})"
    
    def save(self, *args, **kwargs):
        if not self.asset_tag:
            existing_count = Asset.objects.filter(product=self.product).count()
            self.asset_tag = f"{self.product.code}-{existing_count + 1:03d}"
        super().save(*args, **kwargs)


class StockTransaction(models.Model):
    """出入庫紀錄"""
    IN = 'IN'
    OUT = 'OUT'
    TYPE_CHOICES = [
        (IN, '入庫'),
        (OUT, '出庫')
    ]
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, null=True)
    transaction_type = models.CharField(max_length=3, choices=TYPE_CHOICES)
    date = models.DateTimeField(auto_now_add=True)
    remark = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.asset.asset_tag} {self.transaction_type}"
