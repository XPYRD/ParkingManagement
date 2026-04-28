"""
accounts — 序列化器

前后端字段对齐原则：Serializer 输出的 JSON 字段名
必须与 Vue 组件中的 v-model / 模板变量名一一对应。
"""

from rest_framework import serializers
from .models import User, Vehicle


class UserRegisterSerializer(serializers.ModelSerializer):
    """
    用户注册 — 对应 _14/注册页面

    前端表单字段 → Serializer field 映射：
    - 手机号输入框 → phone
    - 设置密码 → password
    - 确认密码 → password_confirm (write_only, 不入库)
    """

    password = serializers.CharField(
        write_only=True, min_length=8, max_length=16,
        help_text='8-16 位强密码'
    )
    password_confirm = serializers.CharField(
        write_only=True,
        help_text='确认密码（需要与 password 一致）'
    )

    class Meta:
        model = User
        fields = ['id', 'phone', 'password', 'password_confirm']

    def validate(self, attrs: dict) -> dict:
        """校验两次密码是否一致"""
        if attrs.get('password') != attrs.pop('password_confirm', None):
            raise serializers.ValidationError({
                'password_confirm': '两次输入的密码不一致'
            })
        return attrs

    def create(self, validated_data: dict) -> User:
        """创建用户 — 使用 set_password 加密"""
        phone = validated_data['phone']
        user = User(
            phone=phone,
            # 手机号同时作为 username，保持 Django 内置认证兼容
            username=phone,
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """
    用户个人信息 — 对应 _5/个人中心

    只读字段：id, username, date_joined
    可写字段：phone, avatar, is_vip
    """

    # 关联车辆数量 — 个人中心(_5)显示的车辆计数
    vehicle_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'phone', 'email', 'avatar',
            'is_vip', 'status', 'is_staff', 'two_factor_enabled', 'date_joined', 'vehicle_count',
        ]
        read_only_fields = ['id', 'username', 'date_joined', 'status', 'is_staff', 'two_factor_enabled']

    def get_vehicle_count(self, obj: User) -> int:
        """获取用户关联车辆数量"""
        return obj.vehicles.count()


class UserAdminSerializer(serializers.ModelSerializer):
    """
    管理端用户列表 — 对应 _10/用户管理表格

    表格列 → 字段映射：
    - 用户名 → username
    - 手机号 → phone
    - 订阅方案 → 通过 Subscription 关联查询（在 ViewSet 中处理）
    - 状态 → status
    - 加入日期 → date_joined
    """

    vehicle_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'phone', 'email', 'avatar',
            'is_vip', 'status', 'is_active', 'date_joined',
            'last_login', 'vehicle_count',
        ]
        read_only_fields = ['id', 'date_joined', 'last_login']

    def get_vehicle_count(self, obj: User) -> int:
        return obj.vehicles.count()


class VehicleSerializer(serializers.ModelSerializer):
    """
    车辆信息 — 对应 _5/车辆管理列表

    卡片字段 → Serializer 映射：
    - 品牌图标 + 名称 → brand + model
    - 车牌号 → plate_number
    - "默认" 标签 → is_primary
    
    新增：energy_type 字段用于选择新能源/油车，系统自动填充其他信息
    """

    # 车主用户名（只读展示）
    owner_name = serializers.CharField(
        source='owner.username', read_only=True
    )
    
    # 能源类型：new_energy（绿牌） | ice（蓝牌）
    energy_type = serializers.CharField(required=False, allow_blank=True, write_only=True)

    class Meta:
        model = Vehicle
        fields = [
            'id', 'owner', 'owner_name', 'plate_number',
            'brand', 'model', 'color', 'is_primary',
            'energy_type', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'owner', 'created_at', 'updated_at']
        extra_kwargs = {
            'brand': {'required': False, 'allow_blank': True},
            'model': {'required': False, 'allow_blank': True},
            'color': {'required': False, 'allow_blank': True},
        }

    def create(self, validated_data: dict) -> Vehicle:
        """
        创建车辆时自动关联当前登录用户，并根据能源类型自动填充信息
        
        逻辑：
        - 用户选择能源类型：new_energy（绿牌）或 ice（蓝牌）
        - 系统自动填充：品牌、型号、颜色
        """
        validated_data['owner'] = self.context['request'].user
        
        # 提取能源类型
        energy_type = validated_data.pop('energy_type', '')
        
        # 根据能源类型自动填充车辆信息
        if energy_type == 'new_energy':
            # 新能源车
            if not validated_data.get('brand'):
                validated_data['brand'] = '新能源车'
            if not validated_data.get('model'):
                validated_data['model'] = '绿牌新能源'
            if not validated_data.get('color'):
                validated_data['color'] = '未知'
        elif energy_type == 'ice':
            # 油车
            if not validated_data.get('brand'):
                validated_data['brand'] = '燃油车'
            if not validated_data.get('model'):
                validated_data['model'] = '蓝牌燃油'
            if not validated_data.get('color'):
                validated_data['color'] = '未知'
        else:
            # 默认填充
            if not validated_data.get('brand'):
                validated_data['brand'] = '未知品牌'
            if not validated_data.get('model'):
                validated_data['model'] = '未知车型'
            if not validated_data.get('color'):
                validated_data['color'] = '未知'
        
        return super().create(validated_data)
