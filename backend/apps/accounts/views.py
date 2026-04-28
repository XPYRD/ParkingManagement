"""
accounts — API 视图

端点清单：
- POST   /api/v1/accounts/register/          用户注册
- GET    /api/v1/accounts/profile/            当前用户信息
- PUT    /api/v1/accounts/profile/            更新个人信息
- GET    /api/v1/accounts/vehicles/           我的车辆列表
- POST   /api/v1/accounts/vehicles/           添加车辆
- GET    /api/v1/accounts/vehicles/{id}/      车辆详情
- PUT    /api/v1/accounts/vehicles/{id}/      更新车辆
- DELETE /api/v1/accounts/vehicles/{id}/      删除车辆
- GET    /api/v1/accounts/admin/users/        [管理端] 用户列表
- GET    /api/v1/accounts/admin/users/{id}/   [管理端] 用户详情
- PATCH  /api/v1/accounts/admin/users/{id}/   [管理端] 修改用户状态
"""

from rest_framework import viewsets, generics, permissions, status
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.response import Response
from rest_framework.decorators import action
import pyotp


from .models import User, Vehicle
from .serializers import (
    UserRegisterSerializer,
    UserProfileSerializer,
    UserAdminSerializer,
    VehicleSerializer,
)


class UserRegisterView(generics.CreateAPIView):
    """
    用户注册 — 对应 _14/注册页面

    POST /api/v1/accounts/register/
    不需要认证，任何人可访问
    """
    serializer_class = UserRegisterSerializer
    permission_classes = [permissions.AllowAny]


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    个人信息 — 对应 _5/个人中心

    GET  /api/v1/accounts/profile/  → 获取当前登录用户信息
    PUT  /api/v1/accounts/profile/  → 更新个人信息（头像、手机号等）
    """
    serializer_class = UserProfileSerializer

    def get_object(self) -> User:
        """始终返回当前登录用户，无需传 ID"""
        return self.request.user


class VehicleViewSet(viewsets.ModelViewSet):
    """
    车辆管理 — 对应 _5/车辆管理列表

    用户只能看到和操作自己的车辆。
    """
    serializer_class = VehicleSerializer

    def get_queryset(self):
        """过滤：只返回当前用户的车辆"""
        return Vehicle.objects.filter(owner=self.request.user)

    @action(detail=True, methods=['post'], url_path='set-primary')
    def set_primary(self, request, pk=None):
        """
        设置默认车辆 — 对应 _5 车辆卡片的 "默认" 标签

        POST /api/v1/accounts/vehicles/{id}/set-primary/
        """
        vehicle = self.get_object()
        # 先将该用户所有车辆的 is_primary 置为 False
        Vehicle.objects.filter(owner=request.user).update(is_primary=False)
        vehicle.is_primary = True
        vehicle.save(update_fields=['is_primary'])
        return Response({'detail': '已设为默认车辆'})


class UserAdminViewSet(viewsets.ModelViewSet):
    """
    [管理端] 用户管理 — 对应 _10/用户管理表格

    仅管理员可访问。支持搜索（用户名/手机号）、筛选（状态/VIP）、排序。
    """
    serializer_class = UserAdminSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = User.objects.filter(is_staff=False)
    filterset_fields = ['status', 'is_vip', 'is_active']
    search_fields = ['username', 'phone', 'email']
    ordering_fields = ['date_joined', 'last_login']

    @action(detail=True, methods=['post'], url_path='toggle-ban')
    def toggle_ban(self, request, pk=None):
        """
        封禁/解封用户 — 对应 _10 表格操作列的 "封禁" 按钮

        POST /api/v1/accounts/admin/users/{id}/toggle-ban/
        """
        user = self.get_object()
        if user.status == User.Status.BANNED:
            user.status = User.Status.ACTIVE
            msg = '用户已解封'
        else:
            user.status = User.Status.BANNED
            msg = '用户已封禁'
        user.save(update_fields=['status'])
        return Response({'detail': msg, 'status': user.status})


class TwoFactorSetupView(generics.GenericAPIView):
    """
    两步验证设置 — 生成 TOTP 密钥
    POST /api/v1/accounts/2fa/setup/
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        # 如果还没生成过密钥，则生成一个 32 位的 Base32 密钥
        if not user.totp_secret:
            user.totp_secret = pyotp.random_base32()
            user.save(update_fields=['totp_secret'])
        
        # 生成 otpauth URL 用于前端生成二维码
        totp = pyotp.TOTP(user.totp_secret)
        otpauth_url = totp.provisioning_uri(
            name=user.username,
            issuer_name="Sentinel Parking"
        )
        
        return Response({
            'secret': user.totp_secret,
            'otpauth_url': otpauth_url
        })


class TwoFactorActivateView(generics.GenericAPIView):
    """
    两步验证激活 — 校验第一个验证码并开启功能
    POST /api/v1/accounts/2fa/activate/
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        otp_code = request.data.get('code')
        user = request.user
        
        if not user.totp_secret:
            return Response({'detail': '请先进行 2FA 设置'}, status=status.HTTP_400_BAD_REQUEST)
        
        totp = pyotp.TOTP(user.totp_secret)
        if totp.verify(otp_code):
            user.two_factor_enabled = True
            user.save(update_fields=['two_factor_enabled'])
            return Response({'detail': '两步验证已成功开启'})
        else:
            return Response({'detail': '验证码不正确'}, status=status.HTTP_400_BAD_REQUEST)


class TwoFactorVerifyView(generics.GenericAPIView):
    """
    两步验证登录核验 — 对应登录第二步
    POST /api/v1/accounts/2fa/verify/
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        otp_code = request.data.get('code')
        
        # 校验基础账号密码
        from django.contrib.auth import authenticate
        user = authenticate(username=username, password=password)
        
        if not user or not user.two_factor_enabled:
            return Response({'detail': '无权访问'}, status=status.HTTP_403_FORBIDDEN)
            
        totp = pyotp.TOTP(user.totp_secret)
        if totp.verify(otp_code):
            # 校验通过，发放正式 Token
            refresh = TokenObtainPairSerializer.get_token(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
        else:
            return Response({'detail': '两步验证码不正确'}, status=status.HTTP_400_BAD_REQUEST)


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    定制化登录接口 — 拦截 2FA
    """
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        
        from django.contrib.auth import authenticate
        user = authenticate(username=username, password=password)
        
        if user and user.two_factor_enabled:
            # 密码正确但开启了 2FA，触发拦截
            return Response({
                'requires_2fa': True,
                'detail': '需输入两步验证码'
            }, status=status.HTTP_200_OK)
            
        return super().post(request, *args, **kwargs)


