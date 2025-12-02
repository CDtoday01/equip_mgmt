from rest_framework import serializers
from users.models import CustomUser
from departments.models import Department

class CustomUserSerializer(serializers.ModelSerializer):
    department = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(),
        required=False,
        allow_null=True
    )
    department_name = serializers.CharField(source="department.name", read_only=True)

    class Meta:
        model = CustomUser
        fields = [
            'id', 'id_number', 'name', 'email', 'phone',
            'title', 'eip_account', 'department', 'department_name','is_active',
        ]
