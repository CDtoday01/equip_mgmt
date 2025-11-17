from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.shortcuts import get_object_or_404
from users.models import CustomUser
from users.serializers import CustomUserSerializer
from departments.models import Department

User = CustomUser  # 避免混淆

@api_view(['GET', 'POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def users_list(request):
    if request.method == 'GET':
        department_name = request.GET.get("department")
        qs = User.objects.all()
        if department_name:
            qs = qs.filter(department__name=department_name)

        serializer = CustomUserSerializer(qs, many=True)
        return Response(serializer.data, status=200)

    elif request.method == 'POST':
        data = request.data
        required_fields = ["id_number", "name", "department", "eip_account"]
        for field in required_fields:
            if not data.get(field):
                return Response({"error": f"缺少必填欄位：{field}"}, status=400)

        if User.objects.filter(id_number=data["id_number"]).exists():
            return Response({"error": "身份證字號已存在"}, status=400)
        if User.objects.filter(eip_account=data["eip_account"]).exists():
            return Response({"error": "EIP帳號已存在"}, status=400)

        department = get_object_or_404(Department, name=data["department"])
        person = User.objects.create(
            id_number=data["id_number"],
            name=data["name"],
            email=data.get("email", ""),
            phone=data.get("phone", ""),
            title=data.get("title", ""),
            eip_account=data.get("eip_account"),
            department=department,
        )
        person.set_password(data["id_number"])
        person.save()

        serializer = CustomUserSerializer(person)
        return Response(serializer.data, status=201)


@api_view(['GET', 'PUT', 'DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def users_detail(request, id_number):
    person = get_object_or_404(User, id_number=id_number)

    if request.method == 'GET':
        serializer = CustomUserSerializer(person)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = CustomUserSerializer(person, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    elif request.method == 'DELETE':
        person.delete()
        return Response({"message": "User deleted successfully"}, status=204)
