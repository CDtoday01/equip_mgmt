from django.contrib.auth import authenticate
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser


# 登入 API（任何人可呼叫）
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    email = request.data.get('email')
    password = request.data.get('password')
    user = authenticate(request, email=email, password=password)

    if user is None:
        print('Invalid credentials')
        return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    # 確保 refresh token 永遠重新發
    refresh = RefreshToken.for_user(user)
    access = refresh.access_token

    return Response({
        'access': str(access),
        'refresh': str(refresh),
        'user': {
            'id': user.id,
            'email': user.email,
            'name': user.name,
        }
    })

def users_list(request):
    if request.method == "GET":
        users = list(CustomUser.objects.values("id", "name", "email"))
        return JsonResponse(users, safe=False)
    else:
        return JsonResponse({"error": "只允許 GET"}, status=405)
