from rest_framework import serializers
from .models import Asset, Product
from django.contrib.auth import get_user_model
from users.serializers import CustomUserSerializer

User = get_user_model()

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'type', 'price']

class AssetSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    owner_user = CustomUserSerializer(read_only=True)
    holder_user = CustomUserSerializer(read_only=True)

    # 可寫入的欄位，用於建立或更新時指定使用者 ID
    owner_user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), write_only=True, required=False
    )
    holder_user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), write_only=True, required=False
    )

    class Meta:
        model = Asset
        fields = ['id', 'asset_tag', 'product', 'owner_user', 'holder_user', 'owner_user_id', 'holder_user_id']
        read_only_fields = ['asset_tag']

    def create(self, validated_data):
        # 把 owner_user_id / holder_user_id 拿出來轉成關聯
        owner = validated_data.pop('owner_user_id', None)
        holder = validated_data.pop('holder_user_id', None)
        asset = super().create(validated_data)
        if owner:
            asset.owner_user = owner
        if holder:
            asset.holder_user = holder
        asset.save()
        return asset

    def update(self, instance, validated_data):
        owner = validated_data.pop('owner_user_id', None)
        holder = validated_data.pop('holder_user_id', None)
        asset = super().update(instance, validated_data)
        if owner is not None:
            asset.owner_user = owner
        if holder is not None:
            asset.holder_user = holder
        asset.save()
        return asset
