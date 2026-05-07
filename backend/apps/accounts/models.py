"""
accounts — 用户与车辆数据模型

数据来源：
- User: _14(注册) + _15(登录) + _5(个人中心) + _10(用户管理后台)
- Vehicle: _5(车辆管理列表) + _3(反向寻车) + _10(关联车辆)
"""

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    自定义用户模型 — 覆盖默认 Django User

    为什么继承 AbstractUser 而非 AbstractBaseUser：
    保留 Django 内置的 username/password/groups/permissions 机制，
    同时扩展手机号、头像等业务字段，减少重复造轮子。

    字段对照：
    ┌──────────────────┬────────────────────────────────────────┐
    │ 字段             │ UI 来源                                 │
    ├──────────────────┼────────────────────────────────────────┤
    │ phone            │ _14 注册页手机号输入框                    │
    │ avatar           │ _5 个人中心头像区域                       │
    │ is_vip           │ _5 通行证状态 "高级会员"                  │
    │ status           │ _10 用户表格"状态"列 (活跃/已封禁)         │
    └──────────────────┴────────────────────────────────────────┘
    """

    class Status(models.TextChoices):
        """用户账户状态 — _10 用户管理表格中的状态标签"""
        ACTIVE = 'active', '活跃'
        BANNED = 'banned', '已封禁'
        INACTIVE = 'inactive', '未激活'

    phone = models.CharField(
        '手机号', max_length=20, unique=True, blank=True, null=True,
        help_text='注册页(_14)中的 11 位手机号码'
    )
    avatar = models.ImageField(
        '头像', upload_to='avatars/', blank=True, null=True,
        help_text='个人中心(_5)用户头像'
    )
    is_vip = models.BooleanField(
        '高级会员', default=False,
        help_text='个人中心(_5)通行证状态标签'
    )
    status = models.CharField(
        '账户状态', max_length=10, choices=Status.choices,
        default=Status.ACTIVE,
        help_text='用户管理(_10)表格中的状态列'
    )
    two_factor_enabled = models.BooleanField(
        '开启两步验证', default=False,
        help_text='是否启用 TOTP 双因子认证'
    )
    totp_secret = models.CharField(
        '2FA 密钥', max_length=32, blank=True, null=True,
        help_text='用于生成 TOTP 二维码的 32 位随机密钥'
    )
    # 不启用“用户直接权限”分配，只保留组权限与超级管理员权限。
    user_permissions = None

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = '用户'
        db_table = 'sentinel_user'

    def __str__(self) -> str:
        return self.username or self.phone or f'User#{self.pk}'


class Vehicle(models.Model):
    """
    用户车辆信息

    字段对照：
    ┌──────────────────┬────────────────────────────────────────┐
    │ 字段             │ UI 来源                                 │
    ├──────────────────┼────────────────────────────────────────┤
    │ owner            │ _5 车辆列表所属用户                       │
    │ plate_number     │ _3 反向寻车搜索框 / _5 车辆卡片车牌号       │
    │ brand            │ _5 车辆卡片品牌名 "特斯拉 Model 3"        │
    │ model            │ _5 车辆卡片型号                           │
    │ color            │ _3 反向寻车结果 "白色"                     │
    │ is_primary       │ _5 车辆卡片 "默认" 标签                   │
    └──────────────────┴────────────────────────────────────────┘
    """

    owner = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='vehicles', verbose_name='车主'
    )
    plate_number = models.CharField(
        '车牌号', max_length=20, unique=True,
        help_text='格式如：京A·12345'
    )
    brand = models.CharField(
        '品牌', max_length=50,
        help_text='如：特斯拉、路虎'
    )
    model = models.CharField(
        '型号', max_length=50, blank=True, default='',
        help_text='如：Model 3、揽胜运动版'
    )
    color = models.CharField(
        '颜色', max_length=20, blank=True, default='',
        help_text='反向寻车结果中的车辆颜色'
    )
    is_primary = models.BooleanField(
        '默认车辆', default=False,
        help_text='个人中心(_5)车辆列表中的"默认"标签'
    )
    is_simulated = models.BooleanField(
        '模拟车辆', default=False,
        help_text='是否通过模拟进场创建的临时车辆，不展示在用户个人车辆列表中'
    )
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '车辆'
        verbose_name_plural = '车辆'
        db_table = 'sentinel_vehicle'
        ordering = ['-is_primary', '-created_at']

    def __str__(self) -> str:
        return f'{self.plate_number} ({self.brand} {self.model})'
