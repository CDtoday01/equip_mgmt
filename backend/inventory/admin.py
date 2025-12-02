from django.contrib import admin
from .models import Product, Asset, StockTransaction

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'type', 'price')
    search_fields = ('code', 'name', 'type')

@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ('asset_tag', 'product', 'owner_user')
    search_fields = ('asset_tag', 'product__name', 'owner_user__name')

@admin.register(StockTransaction)
class StockTransactionAdmin(admin.ModelAdmin):
    list_display = ('asset', 'transaction_type', 'date', 'remark')
    list_filter = ('transaction_type',)