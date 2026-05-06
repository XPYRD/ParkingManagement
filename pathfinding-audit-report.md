# 寻路功能审计报告

**系统**: Sentinel Parking Management  
**审计日期**: 2026-05-05  
**审计范围**: 后端 Dijkstra 导航算法 + 前端备选寻路 + API 层集成

---

## 一、总体评估

寻路系统的核心算法（Dijkstra）实现正确，但存在一个**严重的数据新鲜度缺陷**和若干中低风险的集成/代码质量问题。如果在生产环境中直接使用，导航结果可能在数据库更新后失效。

---

## 二、严重问题

### 1. 导航器单例缓存过期 — 图数据不会随数据库更新而刷新

**位置**: `backend/apps/parking/navigation.py:195-205`

`DijkstraNavigator` 使用模块级单例模式：首个请求到达时构建一次图（加载全部 ParkingSpace 和 SpotConnection），之后所有请求复用同一份内存图。`rebuild_graph()` 方法存在但**没有任何代码路径触发它**——无论通过 API 创建/删除连接（`SpotConnectionViewSet`）、新增车位，还是 `init_parking_map.py` 脚本，都不会通知导航器重建图。

**影响**：
- 管理员通过 API 新增/删除 `SpotConnection` 后，寻路结果不会反映变更
- 新增 `ParkingSpace` 节点后，新节点不在图中，API 会返回 "起点或终点不存在"（实际上在 DB 中已存在，只是不在缓存图里）

**建议修复**：
- 方案 A：在 `SpotConnectionViewSet` 的 `create` / `update` / `destroy` 中调用 `get_navigator().rebuild_graph()`
- 方案 B：使用 Django signals（`post_save` / `post_delete` on `SpotConnection` 和 `ParkingSpace`）自动触发重建
- 方案 C：弃用单例，改为每次请求即时构建图（停车场节点数通常不过千，性能完全可接受）

---

## 三、中等问题

### 2. NavigationPathSerializer 包含错误模型引用

**位置**: `backend/apps/parking/serializers.py:369-374`

```python
def create(self, validated_data: dict) -> Reservation:  # 错误！
    """创建预约时自动关联当前用户 + 生成预约编号"""
    ...
    validated_data['booking_code'] = f'SENT-...'
```

`NavigationPathSerializer` 是一个只读的路径结果序列化器，但其 `create` 方法引用了 `Reservation` 模型，并且生成的是预约编号逻辑。这是从 `ReservationSerializer` 复制粘贴后遗留的代码。由于 `NavigationPathSerializer` 只被用于序列化（不会调用 `create`），当前不会触发运行时错误，但属于代码腐化。

**建议**：删除该方法，或将 Serializer 改为只读。

### 3. 前后端路径查找存在双重实现且行为不一致

- **后端**（`navigation.py`）：基于 DB 中 `SpotConnection` 表的真实拓扑数据，使用堆优化的 Dijkstra
- **前端**（`InteractiveMapWithNavigation.vue:512-575`）：基于纯欧几里得距离 + 300px 阈值构建临时图，使用 O(V²) 的朴素 Dijkstra

差异：
- 前端的图是几何近邻自动生成，可能穿过墙壁/障碍物
- 前端无法访问后端 DB 的 `SpotConnection` 数据，只能使用随机生成的坐标
- `MapView.vue` 正确调用了后端 API（`calculateNavigationPath`），但 `InteractiveMapWithNavigation.vue` 的路由计算从未调用后端接口

**建议**：统一到后端路径查找。如果保留前端备选方案，应让它调用后端 API 作为主路径，仅在离线/失败时回退。

### 4. 后端不返回 `duration` 字段，前端期望读取它

**位置**: `frontend/src/views/user/MapView.vue:718` vs `backend/apps/parking/navigation.py:181-187`

```js
// 前端期望 duration
navigationInfo.value = {
    distance: res.distance,
    duration: res.duration  // ← res 中没有这个字段
}
```

后端 `find_shortest_path()` 的返回值中没有 `duration`，导致前端显示 `undefined`。虽然不会报错，但用户体验受影响。

**建议**：后端增加 `duration` 字段（按步行速度 1.2 m/s 计算），或前端自己根据 `distance` 推算。

### 5. 不支持跨楼层路径查找

`init_parking_map.py` 按楼层独立创建连接（每个楼层内连接每个节点到其最近 5 个邻居）。没有跨楼层的 `SpotConnection`（如连接电梯 B2 ↔ 电梯 B1）。这意味着 `find_path(B2_spot, B1_spot)` 将返回 unreachable。

前端 `MapView.vue` 已经按楼层切换显示（line 783），所以 UI 层面避开了这个问题。但如果未来需求扩展为跨楼层导航，需要补充楼梯/电梯节点间的连接。

---

## 四、低风险/代码质量问题

### 6. 坐标缺失时静默返回零值

**位置**: `backend/apps/parking/navigation.py:64-71`

```python
def _spot_point(spot):
    x = spot.center_x if spot.center_x is not None else spot.x
    y = spot.center_y if spot.center_y is not None else spot.y
    return {'x': float(x) if x is not None else 0.0, 'y': float(y) if y is not None else 0.0}
```

当节点的 `center_x`、`center_y`、`x`、`y` 全部为 None 时，返回 `{x: 0.0, y: 0.0}` —— 一个错误且不明显的坐标。应考虑记录警告日志或抛出异常。

### 7. 步骤重建时的 O(n) 边查找

**位置**: `backend/apps/parking/navigation.py:164-168`

```python
for neighbor, dist in self.graph[path_ids[i]]:
    if neighbor == path_ids[i + 1]:
        edge_distance = dist
        break
```

在重建路径步骤时，需要遍历邻接表来找到对应边的距离，复杂度为 O(degree)。对于停车场规模（每个节点通常 <10 条边）影响可忽略，但如果未来图变大，应考虑在 Dijkstra 主循环中同时记录边距离（例如将 `previous` 数组改为 `(prev_node, edge_distance)` 对）。

### 8. 前端测试数据使用随机坐标

**位置**: `frontend/src/components/InteractiveMapWithNavigation.vue:307-310`

```js
center_x: Math.random() * 900 + 50,
center_y: Math.random() * 700 + 50,
```

`InteractiveMapWithNavigation.vue` 的 `loadMapData()` 在获取后端数据后，将坐标替换为随机值。这显然是开发阶段的遗留代码，导致该组件的前端 Dijkstra 永远基于随机位置计算路径，完全不可用。

### 9. 前端 Dijkstra 起点/终点匹配使用 5px 容差

**位置**: `frontend/src/components/InteractiveMapWithNavigation.vue:526-531`

```js
if (Math.abs(nodes[i].x - start.x) < 5 && Math.abs(nodes[i].y - start.y) < 5) {
    startIdx = i
}
```

使用浮点数绝对容差而非 ID 匹配，在稀有情况下可能匹配到错误的节点或找不到节点。

---

## 五、架构总览

```
用户操作 (MapView.vue / InteractiveMapWithNavigation.vue)
    │
    ├─ [主路径] → calculateNavigationPath() → POST /api/v1/parking/navigation/find-path/
    │                  → NavigationViewSet.find_path()
    │                      → find_path() → get_navigator() → 单例图 (⚠ 可能过期)
    │                          → DijkstraNavigator.find_shortest_path()
    │
    └─ [备选] → InteractiveMapWithNavigation.calculateRoute() → 前端 Dijkstra (⚠ 随机坐标)
```

| 项目 | 后端 | 前端备选 |
|------|------|---------|
| 算法 | 堆优化 Dijkstra | 朴素 Dijkstra O(V²) |
| 图来源 | DB SpotConnection 表 | 几何近邻(<300px) |
| 数据新鲜度 | ❌ 单例过期风险 | 实时但基于随机坐标 |
| 实际可用性 | ✅ 对接真实坐标 | ❌ 仅 Demo |

---

## 六、修复优先级建议

| 优先级 | 问题 | 修复工作量 |
|--------|------|-----------|
| **P0** | 单例缓存过期 — 图不随 DB 更新 | 小（加 signal 或每次重建） |
| **P1** | 后端缺少 `duration` 字段 | 极小（加一行） |
| **P1** | 前端测试随机坐标遗留 | 小（删除覆盖逻辑） |
| **P2** | Serializer 错误模型引用 | 极小（删除方法） |
| **P2** | 坐标缺失时静默零值 | 极小（加日志） |
| **P3** | 前端备选 Dijkstra 统一 | 中（重构为调用后端） |
| **P3** | 跨楼层导航支持 | 中（补充连接数据） |
