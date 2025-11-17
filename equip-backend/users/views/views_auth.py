from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.contrib.auth import authenticate

# ------------------------------
# login
# ------------------------------
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    eip_account = request.data.get('eip_account')
    password = request.data.get('password')
    
    user = authenticate(request, username=eip_account, password=password)
    
    if user is None:
        return Response({'detail': 'Invalid credentials'}, status=401)
    
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
# refresh token
# ------------------------------
@api_view(['POST'])
@permission_classes([AllowAny])
def token_refresh_view(request):
    refresh_token = request.data.get('refresh')
    if not refresh_token:
        return Response({"detail": "Refresh token is required"}, status=400)
    
    try:
        refresh = RefreshToken(refresh_token)
        access = str(refresh.access_token)
        return Response({"access": access})
    except TokenError:
        return Response({"detail": "Invalid refresh token"}, status=401)


# ------------------------------
# logout
# ------------------------------
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """
    登出 API：將 refresh token 加入黑名單，使其失效
    前端需在呼叫後刪掉 localStorage 中的 access/refresh token
    """
    refresh_token = request.data.get('refresh')
    if not refresh_token:
        return Response({"detail": "Refresh token is required"}, status=400)
    
    try:
        token = RefreshToken(refresh_token)
        token.blacklist()  # 將 refresh token 加入黑名單
        return Response({"detail": "Logged out successfully"}, status=200)
    except TokenError:
        return Response({"detail": "Invalid or expired refresh token"}, status=401)
