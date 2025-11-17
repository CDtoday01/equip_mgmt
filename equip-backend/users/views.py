from django.contrib.auth import authenticate
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import TokenError

from .models import CustomUser
from .serializers import CustomUserSerializer
from departments.models import Department


# ------------------------------
# 登入
# ------------------------------
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    eip_account = request.data.get('eip_account')
    password = request.data.get('password')

    user = authenticate(request, username=eip_account, password=password)
    if user is None:
        return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    refresh = RefreshToken.for_user(user)
    access = refresh.access_token

    return Response({
        'access': str(access),
        'refresh': str(refresh),
        'user': {
            'id': user.id,
            'eip_account': user.eip_account,
            'name': user.name,
        }
    })


# ------------------------------
# Refresh token
# ------------------------------
@api_view(['POST'])
@permission_classes([AllowAny])
def token_refresh_view(request):
    refresh_token = request.data.get('refresh')
    if not refresh_token:
        return Response({"detail": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        refresh = RefreshToken(refresh_token)
        access = str(refresh.access_token)
        return Response({"access": access})
    except TokenError:
        return Response({"detail": "Invalid refresh token"}, status=status.HTTP_401_UNAUTHORIZED)


# ------------------------------
# 使用者列表 & 新增
# ------------------------------
@api_view(['GET', 'POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def users_list(request):
    if request.method == 'GET':
        department_name = request.GET.get("department")
        qs = CustomUser.objects.all()
        if department_name:
            qs = qs.filter(department__name=department_name)

        data = [
            {
                "id_number": u.id_number,
                "name": u.name,
                "email": u.email,
                "phone": u.phone,
                "department": u.department.name if u.department else None,
                "title": u.title,
                "eip_account": u.eip_account,
            }
            for u in qs
        ]
        return Response(data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        data = request.data
        required_fields = ["id_number", "name", "department", "eip_account"]
        for field in required_fields:
            if not data.get(field):
                return Response({"error": f"缺少必填欄位：{field}"}, status=status.HTTP_400_BAD_REQUEST)

        if CustomUser.objects.filter(id_number=data["id_number"]).exists():
            return Response({"error": "身份證字號已存在"}, status=status.HTTP_400_BAD_REQUEST)

        if CustomUser.objects.filter(eip_account=data["eip_account"]).exists():
            return Response({"error": "EIP帳號已存在"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            department = Department.objects.get(name=data["department"])
        except Department.DoesNotExist:
            return Response({"error": f"部門 {data['department']} 不存在"}, status=status.HTTP_400_BAD_REQUEST)

        user = CustomUser.objects.create(
            id_number=data["id_number"],
            name=data["name"],
            email=data.get("email", ""),
            phone=data.get("phone", ""),
            title=data.get("title", ""),
            eip_account=data["eip_account"],
            department=department,
        )

        # 密碼預設為身份證字號
        user.set_password(user.id_number)
        user.save()

        return Response({
            "id_number": user.id_number,
            "name": user.name,
            "email": user.email,
            "phone": user.phone,
            "department": user.department.name if user.department else None,
            "title": user.title,
            "eip_account": user.eip_account,
        }, status=status.HTTP_201_CREATED)


# ------------------------------
# 單一使用者 CRUD
# ------------------------------
@api_view(['GET', 'PUT', 'DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def users_detail(request, id_number):
    try:
        user = CustomUser.objects.get(id_number=id_number)
    except CustomUser.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = CustomUserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'PUT':
        serializer = CustomUserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        user.delete()
        return Response({"message": "User deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


# ------------------------------
# 批次匯入 / 更新 / 刪除
# ------------------------------
@api_view(['POST', 'DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def users_bulk(request):
    if request.method == 'POST':
        users_data = request.data
        if not isinstance(users_data, list):
            return Response({"error": "資料格式錯誤，必須是 JSON 陣列"}, status=status.HTTP_400_BAD_REQUEST)

        created_count = 0
        updated_count = 0
        skipped = []

        for entry in users_data:
            try:
                id_number = entry.get("id_number", "").strip()
                eip_account = entry.get("eip_account", "").strip()
                name = entry.get("name", "").strip()
                dept_name = entry.get("department", "").strip()
                title = entry.get("title", "").strip()
                email = entry.get("email", "").strip()
                phone = entry.get("phone", "").strip()

                if not all([id_number, eip_account, name, dept_name]):
                    skipped.append({"entry": entry, "reason": "缺少必填欄位"})
                    continue

                department, _ = Department.objects.get_or_create(name=dept_name)

                user, created = CustomUser.objects.update_or_create(
                    id_number=id_number,
                    defaults={
                        "name": name,
                        "email": email,
                        "phone": phone,
                        "title": title,
                        "eip_account": eip_account,
                        "department": department,
                    }
                )

                # 密碼預設為身份證字號（只在建立時）
                if created:
                    user.set_password(id_number)
                    user.save()

                if created:
                    created_count += 1
                else:
                    updated_count += 1

            except Exception as e:
                skipped.append({"entry": entry, "reason": str(e)})

        return Response({
            "created": created_count,
            "updated": updated_count,
            "skipped": skipped,
        }, status=status.HTTP_200_OK)

    elif request.method == 'DELETE':
        id_numbers = request.data.get("id_numbers")
        if not isinstance(id_numbers, list) or not id_numbers:
            return Response({"error": "請提供 id_numbers 陣列"}, status=status.HTTP_400_BAD_REQUEST)

        deleted = []
        not_found = []

        for id_number in id_numbers:
            try:
                user = CustomUser.objects.get(id_number=id_number)
                user.delete()
                deleted.append(id_number)
            except CustomUser.DoesNotExist:
                not_found.append(id_number)

        return Response({
            "deleted": deleted,
            "not_found": not_found,
            "deleted_count": len(deleted)
        }, status=status.HTTP_200_OK)


# ------------------------------
# 搜尋使用者
# ------------------------------
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def users_search(request):
    name = request.GET.get("name")
    if not name:
        return Response({"error": "請提供 name 參數"}, status=400)

    qs = CustomUser.objects.filter(name__icontains=name)
    data = [
        {
            "id_number": u.id_number,
            "name": u.name,
            "department": u.department.name if u.department else None,
            "email": u.email,
            "phone": u.phone
        }
        for u in qs
    ]
    return Response(data, status=200)
