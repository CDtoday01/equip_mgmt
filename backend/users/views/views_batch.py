from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from users.models import CustomUser
from departments.models import Department

User = CustomUser

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def users_bulk(request):
    """
    統一批量操作：
    - 匯入 / 更新：action="import"，data=[{...}]
    - 轉移部門：action="transfer"，ids=[...], department_id=...
    - 離職：action="retire"，ids=[...]
    """
    data = request.data
    action = data.get("action")

    if action == "import":
        users_data = data.get("data")
        if not isinstance(users_data, list):
            return Response({"error": "資料格式錯誤，必須是 JSON 陣列"}, status=400)

        created_count = 0
        updated_count = 0
        skipped = []

        for entry in users_data:
            try:
                id_number = entry.get("id_number", "").strip()
                eip_account = entry.get("eip_account", "").strip()
                name = entry.get("name", "").strip()
                dept_name = entry.get("department_name", "").strip()
                title = entry.get("title", "").strip()
                email = entry.get("email", "").strip()
                phone = entry.get("phone", "").strip()

                if not all([id_number, eip_account, name, dept_name]):
                    skipped.append({"entry": entry, "reason": "缺少必填欄位"})
                    continue

                department, _ = Department.objects.get_or_create(name=dept_name)
                person, created = User.objects.update_or_create(
                    id_number=id_number,
                    defaults={
                        "name": name,
                        "email": email,
                        "phone": phone,
                        "title": title,
                        "eip_account": eip_account,
                        "department": department,
                        "is_active": True,  # 若之前離職，現在重新入職
                    }
                )
                person.set_password(id_number)
                person.save()

                if created:
                    created_count += 1
                else:
                    updated_count += 1

            except Exception as e:
                skipped.append({"entry": entry, "reason": str(e)})

        return Response({
            "created": created_count,
            "updated": updated_count,
            "skipped": skipped
        })

    elif action == "transfer":
        ids = data.get("ids")
        department_id = data.get("department_id")
        if not ids or not department_id:
            return Response({"error": "請提供 ids 陣列及 department_id"}, status=400)

        try:
            department = Department.objects.get(id=department_id)
        except Department.DoesNotExist:
            return Response({"error": "目標部門不存在"}, status=400)

        updated = []
        not_found = []

        for uid in ids:
            try:
                person = User.objects.get(id=uid)
                person.department = department
                person.save()
                updated.append(uid)
            except User.DoesNotExist:
                not_found.append(uid)

        return Response({
            "updated": updated,
            "not_found": not_found,
            "updated_count": len(updated)
        })

    elif action == "retire":
        ids = data.get("ids")
        if not ids:
            return Response({"error": "請提供 ids 陣列"}, status=400)

        retired = []
        not_found = []

        for uid in ids:
            try:
                person = User.objects.get(id=uid)
                # 假設離職是設定某個欄位，如 is_active=False
                person.is_active = False
                person.save()
                retired.append(uid)
            except User.DoesNotExist:
                not_found.append(uid)

        return Response({
            "retired": retired,
            "not_found": not_found,
            "retired_count": len(retired)
        })

    else:
        return Response({"error": "無效的 action"}, status=400)
