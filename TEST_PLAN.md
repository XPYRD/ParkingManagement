# Sentinel Parking — 系统测试方案

## 一、测试范围与策略

### 当前覆盖现状（41 个后端单元/API 测试）
- accounts: 8 tests (注册、资料、车辆 CRUD)
- parking: 21 tests (车位、预约、会话、导航、AI 识别)
- payments: 12 tests (支付、订阅、定价规则、银行卡)
- dashboard: 12 tests (仪表盘数据、权限)
- devices: 14 tests (设备 CRUD、权限)

### 本次新增测试重点

#### 1. 业务闭环集成测试（E2E 级）
- 完整进出场生命周期：入场 → 查询费用 → 缴费 → 出场
- 完整预约生命周期：选车位 → 预约 → 取消 → 车位释放
- 模拟车辆隔离：模拟进场的车辆不出现在用户"我的车辆"列表

#### 2. 订阅特权边界测试
- 订阅用户进出场免费（amount=0，payment_state=paid）
- 非订阅用户正常计费（按定价规则 hourly_rate × chargeable_hours）
- 订阅用户预约免费（total_amount=0）
- 非订阅用户预约正常收费
- 过期订阅不享受特权
- 其他用户的车不享受 A 用户的订阅

#### 3. 权限安全测试
- 管理员端点普通用户不可访问
- 用户只能看到自己的数据
- 模拟车辆不出现在用户列表

#### 4. 异常与边界测试
- 重复入场（同一车牌第二次进场应被拦截）
- 已出场车辆再次出场
- 取消已取消的预约
- 无权限访问他人数据
- 缺失必填字段

#### 5. 数据一致性测试
- 出场后车位应释放（current_plate 清空）
- 取消预约后车位应释放（reserved_plate 清空）
- 预约创建后车位应标记为 reserved

---

## 二、执行步骤

### Phase 1: 新增集成测试
编写 `backend/apps/integration/tests.py`，覆盖上述 1-5 项新增场景。

### Phase 2: 运行全部测试
运行所有 5 个模块 + 新增集成测试，确认通过。

### Phase 3: 根据测试结果修复问题
针对失败的测试项定位并修复 bug。

### Phase 4: 前端构建验证
确保前端构建通过。

---

## 三、测试结果

### 执行结果：96/96 全部通过

| 模块 | 测试数 | 状态 |
|------|--------|------|
| integration | 31 | ✅ 通过 |
| parking | 21 | ✅ 通过 |
| payments | 12 | ✅ 通过 |
| accounts | 8 | ✅ 通过 |
| dashboard | 12 | ✅ 通过 |
| devices | 14 | ✅ 通过 |

### 修复的问题

1. **Subscription 创建缺 `price` 字段** — `Subscription.price` 是 NOT NULL 字段，集成测试创建时缺少。修复：在 `Subscription.objects.create()` 中添加 `price=Decimal('149.00')`
2. **Webhook URL 名称错误** — 测试使用 `hardware:hardware_webhook_compat`，实际 URL 名称为 `parking:hardware-handle-webhook`
3. **订阅用户预约收费 bug** — 预约验证方法使用 `date or timezone.localdate()` 判断订阅状态，预约日期（如 2026-06-01）超出订阅有效期范围。修复：统一使用 `timezone.localdate()`（当天日期）判断
4. **Quick Pay 创建 Payment 用户为 None** — 匿名请求时 `Payment.user=None` 违反 NOT NULL 约束。修复：回退使用 `session.vehicle.owner`
5. **Webhook 模拟车辆创建 owner 为 AnonymousUser** — `request.user` 未认证时返回 `AnonymousUser`（truthy），导致车辆创建失败。修复：使用 `request.user.is_authenticated` 明确判断
6. **Reservation 直接创建缺 `booking_code`** — 测试使用 `Reservation.objects.create()` 直接创建时未设置唯一的 `booking_code`（unique=True）。修复：每个直接创建都设置唯一编号
7. **Session 列表响应格式** — DRF 分页返回为 `{"results": [...]}` 字典，测试迭代字典得到 key（字符串）。修复：兼容处理分页响应格式
