from rest_framework import serializers
from departments.models import Department
from .models import People

class PeopleSerializer(serializers.ModelSerializer):
    department = serializers.SlugRelatedField(
        queryset=Department.objects.all(),
        slug_field='name',
        required=False,
        allow_null=True
    )

    class Meta:
        model = People
        fields = '__all__'


    def create(self, validated_data):
        # 如果已存在 id_number，就覆蓋
        obj, created = People.objects.update_or_create(
            id_number=validated_data['id_number'],
            defaults=validated_data
        )
        return obj

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
