from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from .models import People
from .serializers import PeopleSerializer
from departments.models import Department
from rest_framework_simplejwt.authentication import JWTAuthentication

@api_view(['GET', 'POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def people_list(request):
    # =========================================================
    # 取得人員列表（GET）
    # =========================================================
    if request.method == 'GET':
        department_name = request.GET.get("department")
        qs = People.objects.all()
        if department_name:
            qs = qs.filter(department__name=department_name)

        data = [
            {
                "id_number": p.id_number,
                "name": p.name,
                "email": p.email,
                "phone": p.phone,
                "department": p.department.name if p.department else None,
                "title": p.title,
                "eip_account": p.eip_account,
            }
            for p in qs
        ]
        return Response(data, status=status.HTTP_200_OK)

    # =========================================================
    # 新增人員（POST）
    # =========================================================
    elif request.method == 'POST':
        data = request.data

        # ---------- 基本驗證 ----------
        required_fields = ["id_number", "name", "department", "eip_account"]
        for field in required_fields:
            if not data.get(field):
                return Response({"error": f"缺少必填欄位：{field}"}, status=status.HTTP_400_BAD_REQUEST)

        # ---------- 檢查重複 ----------
        if People.objects.filter(id_number=data["id_number"]).exists():
            return Response({"error": "身份證字號已存在"}, status=status.HTTP_400_BAD_REQUEST)

        if People.objects.filter(eip_account=data["eip_account"]).exists():
            return Response({"error": "EIP帳號已存在"}, status=status.HTTP_400_BAD_REQUEST)

        # ---------- 取得部門 ----------
        try:
            department = Department.objects.get(name=data["department"])
        except Department.DoesNotExist:
            return Response({"error": f"部門 {data['department']} 不存在"}, status=status.HTTP_400_BAD_REQUEST)

        # ---------- 建立 People ----------
        person = People.objects.create(
            id_number=data["id_number"],
            name=data["name"],
            email=data.get("email", ""),
            phone=data.get("phone", ""),
            title=data.get("title", ""),
            eip_account=data.get("eip_account"),
            department=department,
        )

        # ---------- 建立登入帳號 ----------
        eip_account = data["eip_account"]
        id_number = data["id_number"]

        # 跳過主管理員
        if eip_account.lower() != "admin":
            user, created = User.objects.get_or_create(
                username=eip_account,
                defaults={"email": data.get("email", "")}
            )
            if created:
                user.set_password(id_number)
                user.save()

        return Response({
            "id_number": person.id_number,
            "name": person.name,
            "email": person.email,
            "phone": person.phone,
            "department": person.department.name if person.department else None,
            "title": person.title,
            "eip_account": person.eip_account,
        }, status=status.HTTP_201_CREATED)



# ------------------------------
# 單一人員 CRUD
# ------------------------------
@api_view(['GET', 'PUT', 'DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def people_detail(request, id_number):
    try:
        person = People.objects.get(id_number=id_number)
    except People.DoesNotExist:
        return Response({"error": "People not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = PeopleSerializer(person)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'PUT':
        serializer = PeopleSerializer(person, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        person.delete()
        return Response({"message": "People deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth.models import User
from .models import People
from departments.models import Department

@api_view(['POST', 'DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def people_bulk(request):
# =========================================================
# 批次匯入 / 更新
# =========================================================
    if request.method == 'POST':
        people_data = request.data

        if not isinstance(people_data, list):
            return Response({"error": "資料格式錯誤，必須是 JSON 陣列"}, status=status.HTTP_400_BAD_REQUEST)

        created_count = 0
        updated_count = 0
        skipped = []

        for entry in people_data:
            try:
                id_number = entry.get("id_number", "").strip()
                eip_account = entry.get("eip_account", "").strip()
                name = entry.get("name", "").strip()
                dept_name = entry.get("department", "").strip()
                title = entry.get("title", "").strip()
                email = entry.get("email", "").strip()
                phone = entry.get("phone", "").strip()

                # 檢查必填欄位
                if not all([id_number, eip_account, name, dept_name]):
                    skipped.append({"entry": entry, "reason": "缺少必填欄位"})
                    continue

                # 找部門，如果不存在就建立
                department, _ = Department.objects.get_or_create(name=dept_name)

                # 建立或更新 People
                person, created = People.objects.update_or_create(
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

                # 同步建立 / 更新登入帳號
                if eip_account.lower() != "admin":
                    user, user_created = User.objects.get_or_create(
                        username=eip_account,
                        defaults={"email": email}
                    )
                    if user_created:
                        user.set_password(id_number)
                        user.save()
                    else:
                        user.email = email
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

    # =========================================================
    # 批次刪除
    # =========================================================
    elif request.method == 'DELETE':
        id_numbers = request.data.get("id_numbers")
        if not isinstance(id_numbers, list) or not id_numbers:
            return Response({"error": "請提供 id_numbers 陣列"}, status=status.HTTP_400_BAD_REQUEST)

        deleted = []
        not_found = []

        for id_number in id_numbers:
            try:
                person = People.objects.get(id_number=id_number)
                eip_account = person.eip_account
                person.delete()
                deleted.append(id_number)

                # 同步刪除帳號（非 admin）
                if eip_account and eip_account.lower() != "admin":
                    User.objects.filter(username=eip_account).delete()

            except People.DoesNotExist:
                not_found.append(id_number)

        return Response({
            "deleted": deleted,
            "not_found": not_found,
            "deleted_count": len(deleted)
        }, status=status.HTTP_200_OK)


# ------------------------------
# 搜尋員工
# ------------------------------
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def people_search(request):
    name = request.GET.get("name")
    if not name:
        return Response({"error": "請提供 name 參數"}, status=400)

    qs = People.objects.filter(name__icontains=name)
    data = [
        {
            "id_number": p.id_number,
            "name": p.name,
            "department": p.department.name if p.department else None,
            "email": p.email,
            "phone": p.phone
        }
        for p in qs
    ]
    return Response(data, status=200)
