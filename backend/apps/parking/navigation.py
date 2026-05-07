"""
navigation.py — 基于道路网络的 Dijkstra 最短路径规划

停车场路径规划规则：
1. 路径只能在道路（走廊）上通行
2. 不能穿过车位或障碍物
3. 每个车位从"空闲侧"边缘离开，不穿过其他车位
4. 路径 = 起点车位 → 出口边 → 走廊 → 终点车位

车位布局（DB center_x / center_y）:
  主区域（X=196~769, Y=327~665）: 4 行 × 多列
    Y 行: 327(上) / 409(中上) / 584(中下) / 665(下)
    X 列: 196 / 247 / 299 / 350 / 401 / 452 / 513 / 565 / 616 / 667 / 718 / 769
  右侧区域（X=993）: Y=249~793 多行
  顶部区域（Y=86）:   X=238~494
  测试车位（X=100~200, Y=100）: 左侧

走廊设计:
  主垂直走廊: x=881（在 X=769 和 X=993 之间）
  左侧走廊:   x=140（仅在 X=196 左侧，不延伸到主区域内部）
  水平走廊1:  y=368（Y=327 和 Y=409 之间）—— 分为主区域段和左侧段
  水平走廊2:  y=496（Y=409 和 Y=584 之间）
  水平走廊3:  y=624（Y=584 和 Y=665 之间）
  顶部走廊:   y=50（Y=86 上方）
  底部走廊:   y=820（Y=793 下方）

关键设计：水平走廊不穿过车位行，只存在于车位之间的空隙中
"""

import heapq
import math
from typing import Dict, List, Tuple, Optional

from .models import ParkingSpace, SpotConnection


# ============================================================
# 走廊参数
# ============================================================
VERT_ROAD_X = 881       # 主垂直走廊（X=769 和 X=993 之间）
LEFT_ROAD_X = 140       # 左侧走廊（X=196 左侧，仅供测试车位使用）
H_ROADS_Y = [368, 496, 624]  # 水平走廊（行间距中点）
TOP_ROAD_Y = 50         # 顶部走廊
BOTTOM_ROAD_Y = 820     # 底部走廊

# 主区域边界
MAIN_X_MIN = 196        # 主区域最左车位中心
MAIN_X_MAX = 769        # 主区域最右车位中心
HALF_W = 46.6 / 2       # 车位半宽
HALF_H = 78.4 / 2       # 车位半高


def _get_road_nodes(floor: str) -> List[Dict]:
    """
    返回指定楼层的道路节点列表。

    水平走廊分为两段：
    - 主区域段：从 x=VERT_ROAD_X 到主区域右边界（不穿过车位）
    - 左侧段：从 x=LEFT_ROAD_X 到主区域左边界（仅供左侧车位使用）
    主区域段和左侧段之间不直接连接（中间被车位行阻断）
    """
    nodes = []

    # --- 主垂直走廊上的节点 ---
    for ry in H_ROADS_Y + [TOP_ROAD_Y, BOTTOM_ROAD_Y]:
        nodes.append({
            'id': f'road_{floor}_{VERT_ROAD_X}x{ry}',
            'x': float(VERT_ROAD_X),
            'y': float(ry),
            'type': 'main_intersection',
        })

    # 垂直走廊上的中间点（保证连通性）
    all_road_ys = sorted(H_ROADS_Y + [TOP_ROAD_Y, BOTTOM_ROAD_Y])
    for i in range(len(all_road_ys) - 1):
        mid_y = (all_road_ys[i] + all_road_ys[i + 1]) / 2
        nodes.append({
            'id': f'road_v_{floor}_{VERT_ROAD_X}y{int(mid_y)}',
            'x': float(VERT_ROAD_X),
            'y': float(mid_y),
            'type': 'vertical',
        })

    # --- 水平走廊：主区域段（从主区域右边缘到主垂直走廊） ---
    # 水平走廊从 MAIN_X_MAX + HALF_W 到 VERT_ROAD_X，不穿过车位
    main_road_start_x = MAIN_X_MAX + HALF_W  # ~792.3
    for ry in H_ROADS_Y:
        # 主区域段：右端点（在 VERT_ROAD_X）
        nodes.append({
            'id': f'road_h_main_{floor}_{ry}_right',
            'x': float(VERT_ROAD_X),
            'y': float(ry),
            'type': 'horizontal_main',
        })
        # 中间点
        mid_x = (main_road_start_x + VERT_ROAD_X) / 2
        nodes.append({
            'id': f'road_h_main_{floor}_{ry}_mid',
            'x': float(mid_x),
            'y': float(ry),
            'type': 'horizontal_main',
        })
        # 左端点（主区域右边缘外侧）
        nodes.append({
            'id': f'road_h_main_{floor}_{ry}_left',
            'x': float(main_road_start_x),
            'y': float(ry),
            'type': 'horizontal_main',
        })

    # --- 水平走廊：顶部/底部段（从左侧走廊到主垂直走廊，不被车位阻断） ---
    for ry in (TOP_ROAD_Y, BOTTOM_ROAD_Y):
        nodes.append({
            'id': f'road_h_{floor}_{ry}_left',
            'x': float(LEFT_ROAD_X),
            'y': float(ry),
            'type': 'horizontal',
        })
        # 中间点
        mid_x = (LEFT_ROAD_X + VERT_ROAD_X) / 2
        nodes.append({
            'id': f'road_h_{floor}_{ry}_mid',
            'x': float(mid_x),
            'y': float(ry),
            'type': 'horizontal',
        })

    # --- 左侧走廊节点（仅顶部/底部交叉口） ---
    for ry in (TOP_ROAD_Y, BOTTOM_ROAD_Y):
        nodes.append({
            'id': f'road_left_{floor}_{ry}',
            'x': float(LEFT_ROAD_X),
            'y': float(ry),
            'type': 'left_vertical',
        })

    # 左侧走廊中间点（顶部到底部）
    mid_y_left = (TOP_ROAD_Y + BOTTOM_ROAD_Y) / 2
    nodes.append({
        'id': f'road_left_{floor}_mid',
        'x': float(LEFT_ROAD_X),
        'y': float(mid_y_left),
        'type': 'left_vertical',
    })

    return nodes


def _dist(x1: float, y1: float, x2: float, y2: float) -> float:
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


class RoadNavigator:
    """
    基于道路网络的停车场导航器。
    路径只在走廊上通行，不穿过车位或障碍物。
    """

    def __init__(self):
        self.spots: Dict[int, ParkingSpace] = {}
        self.spots_by_floor: Dict[str, Dict[int, ParkingSpace]] = {}
        self.road_nodes: Dict[str, List[Dict]] = {}
        self.graph: Dict[str, List[Tuple[str, float]]] = {}
        self.coords: Dict[str, Tuple[float, float]] = {}
        self._build()

    def _spot_xy(self, spot: ParkingSpace) -> Tuple[float, float]:
        x = spot.center_x if spot.center_x is not None else (spot.x or 0)
        y = spot.center_y if spot.center_y is not None else (spot.y or 0)
        return float(x), float(y)

    def _build(self):
        """构建道路网络图。"""
        all_spots = list(ParkingSpace.objects.all().select_related())
        self.spots = {spot.id: spot for spot in all_spots}

        self.spots_by_floor = {}
        for spot in all_spots:
            self.spots_by_floor.setdefault(spot.floor, {})[spot.id] = spot

        for floor in ('B2', 'B1', '1F'):
            self.road_nodes[floor] = _get_road_nodes(floor)

        self.graph = {}
        self.coords = {}

        # 添加道路节点到图
        for floor, nodes in self.road_nodes.items():
            for node in nodes:
                nid = node['id']
                self.graph[nid] = []
                self.coords[nid] = (node['x'], node['y'])

        # --- 连接道路节点 ---
        for floor in ('B2', 'B1', '1F'):
            road_nodes = self.road_nodes[floor]

            h_nodes_by_y: Dict[float, List[Dict]] = {}
            v_nodes_by_x: Dict[float, List[Dict]] = {}
            for node in road_nodes:
                if node['type'] in ('main_intersection', 'horizontal_main'):
                    h_nodes_by_y.setdefault(node['y'], []).append(node)
                    v_nodes_by_x.setdefault(node['x'], []).append(node)
                elif node['type'] == 'vertical':
                    v_nodes_by_x.setdefault(node['x'], []).append(node)
                elif node['type'] == 'horizontal':
                    h_nodes_by_y.setdefault(node['y'], []).append(node)
                    v_nodes_by_x.setdefault(node['x'], []).append(node)
                elif node['type'] == 'left_vertical':
                    v_nodes_by_x.setdefault(node['x'], []).append(node)

            # 水平走廊段：同 Y 的节点按 X 排序后相邻连接
            for y_val, nodes_at_y in h_nodes_by_y.items():
                sorted_nodes = sorted(nodes_at_y, key=lambda n: n['x'])
                for i in range(len(sorted_nodes) - 1):
                    a, b = sorted_nodes[i], sorted_nodes[i + 1]
                    d = _dist(a['x'], a['y'], b['x'], b['y'])
                    self.graph[a['id']].append((b['id'], round(d, 2)))
                    self.graph[b['id']].append((a['id'], round(d, 2)))

            # 垂直走廊：同 X 的节点按 Y 排序后相邻连接
            for x_val, nodes_at_x in v_nodes_by_x.items():
                sorted_nodes = sorted(nodes_at_x, key=lambda n: n['y'])
                for i in range(len(sorted_nodes) - 1):
                    a, b = sorted_nodes[i], sorted_nodes[i + 1]
                    d = _dist(a['x'], a['y'], b['x'], b['y'])
                    self.graph[a['id']].append((b['id'], round(d, 2)))
                    self.graph[b['id']].append((a['id'], round(d, 2)))

        # --- 跨楼层连接（电梯） ---
        elevator_positions = []
        for node in self.road_nodes['B2']:
            if node['type'] == 'main_intersection':
                elevator_positions.append((node['x'], node['y']))

        for ex, ey in elevator_positions:
            prev_node_id = None
            for floor in ('B2', 'B1', '1F'):
                closest = None
                min_d = float('inf')
                for node in self.road_nodes[floor]:
                    d = _dist(ex, ey, node['x'], node['y'])
                    if d < min_d:
                        min_d = d
                        closest = node
                if closest and min_d < 5:
                    if prev_node_id:
                        self.graph[closest['id']].append((prev_node_id, 10.0))
                        self.graph[prev_node_id].append((closest['id'], 10.0))
                    prev_node_id = closest['id']

        # --- 车位连接到道路网络 ---
        # 根据车位位置判断从哪个方向离开：
        #   主区域车位（x=196~769）→ 向 RIGHT 走到主垂直走廊 x=881
        #   右侧车位（x=993）→ 向 LEFT 走到主垂直走廊 x=881
        #   左侧车位（x < 173）→ 向 LEFT 走到左侧走廊 x=140
        # 上下方向：根据车位所在行与水平走廊的相对位置决定

        for spot in all_spots:
            sx, sy = self._spot_xy(spot)
            floor_nodes = self.road_nodes.get(spot.floor, [])
            if not floor_nodes:
                continue

            spot_left = sx - HALF_W
            spot_right = sx + HALF_W
            spot_top = sy - HALF_H
            spot_bottom = sy + HALF_H

            # 判断车位属于哪一类，确定出口走廊
            if sx > 900:
                # 右侧区域车位（x=993）→ 向左走到主垂直走廊
                spot_category = 'right'
            elif sx < 173:
                # 左侧车位（测试车位）→ 向左走到左侧走廊
                spot_category = 'left'
            else:
                # 主区域车位 → 向右走到主垂直走廊
                spot_category = 'main'

            # 找到最近的水平走廊（上或下）
            nearest_h_road_y = None
            min_y_dist = float('inf')
            for ry in H_ROADS_Y:
                # 水平走廊必须在车位行的间隙中（不穿过车位）
                d = abs(ry - sy)
                if d < min_y_dist:
                    min_y_dist = d
                    nearest_h_road_y = ry

            # 收集该车位应连接的道路节点
            candidates = []
            for node in floor_nodes:
                nx, ny = node['x'], node['y']
                if spot_category == 'main':
                    # 主区域车位：只连接到右侧的走廊节点
                    # 水平方向：节点在车位右侧 (nx > spot_right)
                    # 垂直方向：连接到水平走廊段（main_intersection 或 horizontal_main）
                    if nx > spot_right and node['type'] in ('main_intersection', 'horizontal_main', 'vertical'):
                        candidates.append(node)
                elif spot_category == 'right':
                    # 右侧车位：连接到左侧的主垂直走廊
                    if nx < spot_left and node['type'] in ('main_intersection', 'vertical'):
                        candidates.append(node)
                elif spot_category == 'left':
                    # 左侧车位：连接到左侧走廊或水平走廊的左侧段
                    if node['type'] in ('left_vertical', 'horizontal'):
                        candidates.append(node)

            if not candidates:
                # 回退：连接到任意最近的节点
                distances = []
                for node in floor_nodes:
                    md = abs(sx - node['x']) + abs(sy - node['y'])
                    distances.append((md, node))
                distances.sort(key=lambda x: x[0])
                candidates = [n for _, n in distances[:4]]

            spot_id = str(spot.id)
            if spot_id not in self.graph:
                self.graph[spot_id] = []
                self.coords[spot_id] = (sx, sy)

            # 对每个候选道路节点，创建 2 个拐点连接到车位
            for node in candidates[:4]:
                nx, ny = node['x'], node['y']

                # 根据节点方向确定出口边和路径
                if ny < spot_top:
                    # 节点在车位上方 → 从上边出去
                    edge_x, edge_y = sx, spot_top
                    corridor_x, corridor_y = nx, spot_top
                elif ny > spot_bottom:
                    # 节点在车位下方 → 从下边出去
                    edge_x, edge_y = sx, spot_bottom
                    corridor_x, corridor_y = nx, spot_bottom
                elif nx < spot_left:
                    # 节点在车位左侧 → 从左边出去
                    edge_x, edge_y = spot_left, sy
                    corridor_x, corridor_y = spot_left, ny
                elif nx > spot_right:
                    # 节点在车位右侧 → 从右边出去
                    edge_x, edge_y = spot_right, sy
                    corridor_x, corridor_y = spot_right, ny
                else:
                    # 默认
                    if ny < sy:
                        edge_x, edge_y = sx, spot_top
                        corridor_x, corridor_y = nx, spot_top
                    else:
                        edge_x, edge_y = sx, spot_bottom
                        corridor_x, corridor_y = nx, spot_bottom

                turn1_id = f't1_{spot_id}_{node["id"]}'
                turn2_id = f't2_{spot_id}_{node["id"]}'
                self.coords[turn1_id] = (edge_x, edge_y)
                self.coords[turn2_id] = (corridor_x, corridor_y)
                self.graph[turn1_id] = []
                self.graph[turn2_id] = []

                d1 = abs(sx - edge_x) + abs(sy - edge_y)
                self.graph[spot_id].append((turn1_id, round(d1, 2)))
                self.graph[turn1_id].append((spot_id, round(d1, 2)))

                d2 = abs(edge_x - corridor_x) + abs(edge_y - corridor_y)
                self.graph[turn1_id].append((turn2_id, round(d2, 2)))
                self.graph[turn2_id].append((turn1_id, round(d2, 2)))

                d3 = abs(corridor_x - nx) + abs(corridor_y - ny)
                self.graph[turn2_id].append((node['id'], round(d3, 2)))
                self.graph[node['id']].append((turn2_id, round(d3, 2)))

        # 显式连接（SpotConnection）优先级最高
        for conn in SpotConnection.objects.select_related('from_spot', 'to_spot').all():
            from_id = str(conn.from_spot.id)
            to_id = str(conn.to_spot.id)
            if from_id in self.graph and to_id in self.graph:
                existing = any(nid == to_id for nid, _ in self.graph[from_id])
                if not existing:
                    self.graph[from_id].append((to_id, round(conn.distance, 2)))
                    self.graph[to_id].append((from_id, round(conn.distance, 2)))

    def _display_name(self, spot: ParkingSpace) -> str:
        if spot.node_type == ParkingSpace.NodeType.LOCATION:
            return spot.location_name or spot.space_id
        return spot.space_id

    def find_shortest_path(
        self, start_spot_id: int, end_spot_id: int
    ) -> Optional[Dict]:
        start_sid = str(start_spot_id)
        end_sid = str(end_spot_id)

        if start_spot_id not in self.spots or end_spot_id not in self.spots:
            return None

        if start_sid == end_sid:
            spot = self.spots[start_spot_id]
            sx, sy = self._spot_xy(spot)
            return {
                'path': [self._display_name(spot)],
                'path_node_ids': [spot.space_id],
                'path_points': [{'x': sx, 'y': sy}],
                'distance': 0.0,
                'steps': []
            }

        distances = {node: float('inf') for node in self.graph}
        distances[start_sid] = 0.0
        previous = {node: None for node in self.graph}
        pq = [(0.0, start_sid)]
        visited = set()

        while pq:
            current_distance, current_node = heapq.heappop(pq)
            if current_node in visited:
                continue
            visited.add(current_node)
            if current_node == end_sid:
                break
            for neighbor, edge_distance in self.graph.get(current_node, []):
                if neighbor in visited:
                    continue
                new_distance = current_distance + edge_distance
                if new_distance < distances[neighbor]:
                    distances[neighbor] = new_distance
                    previous[neighbor] = current_node
                    heapq.heappush(pq, (new_distance, neighbor))

        if distances[end_sid] == float('inf'):
            return None

        path_ids = []
        current = end_sid
        while current is not None:
            path_ids.append(current)
            current = previous[current]
        path_ids.reverse()

        # 构建原始路径点列表（去重连续相同坐标）
        raw_points = []
        prev_point = None
        is_location_start = False

        # 检查起点是否为出入口类公共位置
        if int(start_sid) in self.spots:
            start_spot = self.spots[int(start_sid)]
            if start_spot.node_type == ParkingSpace.NodeType.LOCATION:
                is_location_start = True

        for idx, nid in enumerate(path_ids):
            if nid in self.spots:
                spot = self.spots[int(nid)]
                name = self._display_name(spot)
                x, y = self.coords[nid]
            else:
                name = nid
                x, y = self.coords[nid]

            # 起点为出入口等公共位置时，路径从标记底部出发
            if is_location_start and nid == start_sid:
                y = y + 16

            point = (round(x, 1), round(y, 1))
            if point == prev_point:
                continue
            prev_point = point
            raw_points.append({
                'name': name,
                'node_id': nid if nid not in self.spots else self.spots[int(nid)].space_id,
                'x': x, 'y': y,
            })

        # 去除共线冗余点（三点在同一直线上时移除中间点）
        # 出入口起点的首个点不参与剔除，确保路径从标记底部出发
        cleaned = list(raw_points)
        changed = True
        min_check_idx = 1 if is_location_start else 0
        while changed and len(cleaned) >= 3:
            changed = False
            i = min_check_idx
            while i < len(cleaned) - 1:
                p0, p1, p2 = cleaned[i-1], cleaned[i], cleaned[i+1]
                # 三点共线：X 都相同 或 Y 都相同
                if (abs(p0['x'] - p1['x']) < 0.5 and abs(p1['x'] - p2['x']) < 0.5) or \
                   (abs(p0['y'] - p1['y']) < 0.5 and abs(p1['y'] - p2['y']) < 0.5):
                    cleaned.pop(i)
                    changed = True
                else:
                    i += 1

        path_spots = [p['name'] for p in cleaned]
        path_node_ids = [p['node_id'] for p in cleaned]
        path_points = [{'x': p['x'], 'y': p['y']} for p in cleaned]

        steps = []
        for i in range(len(path_ids) - 1):
            from_id = path_ids[i]
            to_id = path_ids[i + 1]
            edge_distance = None
            for neighbor, dist in self.graph.get(from_id, []):
                if neighbor == to_id:
                    edge_distance = dist
                    break
            if edge_distance is None:
                fx, fy = self.coords[from_id]
                tx, ty = self.coords[to_id]
                edge_distance = round(_dist(fx, fy, tx, ty), 2)

            if from_id in self.spots:
                from_name = self._display_name(self.spots[int(from_id)])
                from_sid = self.spots[int(from_id)].space_id
            else:
                from_name = from_id
                from_sid = from_id

            if to_id in self.spots:
                to_name = self._display_name(self.spots[int(to_id)])
                to_sid = self.spots[int(to_id)].space_id
            else:
                to_name = to_id
                to_sid = to_id

            fx, fy = self.coords[from_id]
            tx, ty = self.coords[to_id]

            steps.append({
                'from_id': from_sid,
                'to_id': to_sid,
                'from': from_name,
                'to': to_name,
                'distance': float(edge_distance),
                'from_coords': {'x': fx, 'y': fy},
                'to_coords': {'x': tx, 'y': ty},
            })

        return {
            'path': path_spots,
            'path_node_ids': path_node_ids,
            'path_points': path_points,
            'distance': round(distances[end_sid], 2),
            'steps': steps
        }


def find_path(start_spot_id: int, end_spot_id: int) -> Optional[Dict]:
    navigator = RoadNavigator()
    return navigator.find_shortest_path(start_spot_id, end_spot_id)


def find_path_by_spot_code(start_code: str, end_code: str) -> Optional[Dict]:
    try:
        start_spot = ParkingSpace.objects.get(space_id=start_code)
        end_spot = ParkingSpace.objects.get(space_id=end_code)
        return find_path(start_spot.id, end_spot.id)
    except ParkingSpace.DoesNotExist:
        return None
