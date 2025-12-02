from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Department
from .serializers import DepartmentSerializer

# 列表 + 新增
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def departments_list(request):
    if request.method == 'GET':
        depts = Department.objects.all()
        serializer = DepartmentSerializer(depts, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = DepartmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

# 詳細 GET / PUT / DELETE
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def department_detail(request, dept_id):
    try:
        dept = Department.objects.get(id=dept_id)
    except Department.DoesNotExist:
        return Response({"error": "Department not found"}, status=404)

    if request.method == 'GET':
        serializer = DepartmentSerializer(dept)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = DepartmentSerializer(dept, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    elif request.method == 'DELETE':
        dept.delete()
        return Response(status=204)
