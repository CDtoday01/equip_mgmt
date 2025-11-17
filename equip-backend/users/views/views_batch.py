from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.shortcuts import get_object_or_404
from users.models import CustomUser
from departments.models import Department

User = CustomUser

@api_view(['POST', 'DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def users_bulk(request):
    if request.method == 'POST':
        users_data = request.data
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
                dept_name = entry.get("department", "").strip()
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

    elif request.method == 'DELETE':
        id_numbers = request.data.get("id_numbers")
        if not isinstance(id_numbers, list) or not id_numbers:
            return Response({"error": "請提供 id_numbers 陣列"}, status=400)

        deleted = []
        not_found = []

        for id_number in id_numbers:
            try:
                person = User.objects.get(id_number=id_number)
                person.delete()
                deleted.append(id_number)
            except User.DoesNotExist:
                not_found.append(id_number)

        return Response({
            "deleted": deleted,
            "not_found": not_found,
            "deleted_count": len(deleted)
        })
