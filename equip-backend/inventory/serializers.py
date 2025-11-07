from rest_framework import serializers
from people.serializers import PeopleSerializer
from .models import Asset, Product
from django.contrib.auth import get_user_model

User = get_user_model()

class HolderSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name']

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'type', 'price']

class AssetSerializer(serializers.ModelSerializer):
    # 直接用 ProductSerializer 取代 product 欄位
    product = ProductSerializer(read_only=True)
    owner_user = PeopleSerializer(read_only=True)

    class Meta:
        model = Asset
        fields = ['id', 'asset_tag', 'product', 'owner_user']
        read_only_fields = ['asset_tag']
