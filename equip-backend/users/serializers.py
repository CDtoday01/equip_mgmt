from rest_framework import serializers
from users.models import CustomUser

class CustomUserSerializer(serializers.ModelSerializer):
    department = serializers.StringRelatedField()  # 顯示部門名稱

    class Meta:
        model = CustomUser
        fields = ['id_number', 'name', 'email', 'phone', 'title', 'eip_account', 'department']
