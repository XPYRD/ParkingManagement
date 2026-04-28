"""
init_parking_map.py — 初始化停车场地图拓扑结构

使用方式：
    python manage.py shell < apps/parking/init_parking_map.py

该脚本创建停车位之间的连接关系，用于 Dijkstra 路径规划算法。
"""

import math
from parking.models import ParkingSpace, SpotConnection

# 清除旧的连接关系
SpotConnection.objects.all().delete()

# 获取所有真实停车位和地理标记
all_nodes = ParkingSpace.objects.all()
print(f"已加载 {all_nodes.count()} 个节点")

# 获取唯一的楼层
floors = set(obj.floor for obj in all_nodes if obj.floor)
print(f"楼层列表: {sorted(floors)}")

for floor in sorted(floors):
    floor_nodes = list(all_nodes.filter(floor=floor))
    
    if not floor_nodes:
        continue
    
    print(f"\n处理楼层: {floor} ({len(floor_nodes)} 个节点)")
    
    # 建立一个联通图：每个节点连接到最近的 5 个有效节点
    for current_node in floor_nodes:
        distances = []
        for other_node in floor_nodes:
            if current_node.id == other_node.id:
                continue
            
            # 使用 center_x 和 center_y 计算欧几里得距离
            if current_node.center_x is not None and current_node.center_y is not None and other_node.center_x is not None and other_node.center_y is not None:
                dist = math.sqrt(
                    (current_node.center_x - other_node.center_x) ** 2 +
                    (current_node.center_y - other_node.center_y) ** 2
                )
                distances.append((dist, other_node))
            else:
                distances.append((9999.0, other_node))
                
        # 排序并取最近的 5 个点建立双向连接
        distances.sort(key=lambda x: x[0])
        nearest_neighbors = distances[:5]
        
        for dist, next_node in nearest_neighbors:
            # 创建双向连接
            SpotConnection.objects.get_or_create(
                from_spot=current_node,
                to_spot=next_node,
                defaults={'distance': round(dist, 2)}
            )
            SpotConnection.objects.get_or_create(
                from_spot=next_node,
                to_spot=current_node,
                defaults={'distance': round(dist, 2)}
            )

    print(f"  楼层 {floor}: 已处理连接")

print(f"\n✓ 初始化完成！总共创建 {SpotConnection.objects.count()} 对连接")
print(f"可以通过 API 测试路径规划：POST /api/v1/parking/navigation/find-path/")
