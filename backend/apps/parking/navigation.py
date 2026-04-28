"""
navigation.py — Dijkstra 最短路径规划算法

实现停车场地图中两个停车位之间的最优导航路径
"""

import heapq
from typing import Dict, List, Tuple, Optional

from .models import ParkingSpace, SpotConnection


class DijkstraNavigator:
    """
    使用 Dijkstra 算法计算停车场中的最短路径
    """

    def __init__(self):
        """初始化图数据结构"""
        self.graph: Dict[int, List[Tuple[int, float]]] = {}
        self.spots: Dict[int, ParkingSpace] = {}
        self._build_graph()

    def _build_graph(self):
        """
        从数据库构建图的邻接表表示
        
        形式：
        {
            spot_id_1: [(spot_id_2, distance), (spot_id_3, distance), ...],
            spot_id_2: [(spot_id_1, distance), ...],
            ...
        }
        """
        # 获取所有停车位
        all_spots = ParkingSpace.objects.all()
        self.spots = {spot.id: spot for spot in all_spots}

        # 初始化每个停车位的邻接表
        for spot_id in self.spots.keys():
            self.graph[spot_id] = []

        # 从数据库加载所有连接关系
        connections = SpotConnection.objects.select_related(
            'from_spot', 'to_spot'
        ).all()

        for conn in connections:
            from_id = conn.from_spot.id
            to_id = conn.to_spot.id
            distance = conn.distance

            # 添加双向边（如果需要单向，只保留第一行）
            self.graph[from_id].append((to_id, distance))
            self.graph[to_id].append((from_id, distance))

    @staticmethod
    def _display_name(spot: ParkingSpace) -> str:
        if spot.node_type == ParkingSpace.NodeType.LOCATION:
            return spot.location_name or spot.space_id
        return spot.space_id

    @staticmethod
    def _spot_point(spot: ParkingSpace) -> Dict[str, float]:
        """Prefer center coordinates for navigation rendering, fallback to x/y."""
        x = spot.center_x if spot.center_x is not None else spot.x
        y = spot.center_y if spot.center_y is not None else spot.y
        return {
            'x': float(x) if x is not None else 0.0,
            'y': float(y) if y is not None else 0.0,
        }

    def find_shortest_path(
        self, start_spot_id: int, end_spot_id: int
    ) -> Optional[Dict]:
        """
        计算从起点到终点的最短路径

        Args:
            start_spot_id: 起点停车位 ID
            end_spot_id: 终点停车位 ID

        Returns:
            {
                'path': [A-01, A-02, B-02, ...],       # 停车位编号序列
                'distance': 45.5,                       # 总距离（米）
                'steps': [
                    {'from': 'A-01', 'to': 'A-02', 'distance': 1.5},
                    {'from': 'A-02', 'to': 'B-02', 'distance': 2.0},
                    ...
                ]
            }
            或 None 如果不存在路径
        """
        if start_spot_id not in self.spots or end_spot_id not in self.spots:
            return None

        if start_spot_id == end_spot_id:
            spot = self.spots[start_spot_id]
            return {
                'path': [self._display_name(spot)],
                'distance': 0.0,
                'steps': []
            }

        # 初始化距离和前驱节点
        distances = {node: float('inf') for node in self.graph}
        distances[start_spot_id] = 0.0
        previous = {node: None for node in self.graph}

        # 优先队列：(距离, 节点ID)
        pq = [(0.0, start_spot_id)]

        visited = set()

        while pq:
            current_distance, current_node = heapq.heappop(pq)

            if current_node in visited:
                continue

            visited.add(current_node)

            # 到达终点
            if current_node == end_spot_id:
                break

            # 遍历邻接节点
            for neighbor, edge_distance in self.graph[current_node]:
                if neighbor in visited:
                    continue

                new_distance = current_distance + edge_distance

                if new_distance < distances[neighbor]:
                    distances[neighbor] = new_distance
                    previous[neighbor] = current_node
                    heapq.heappush(pq, (new_distance, neighbor))

        # 如果终点不可达
        if distances[end_spot_id] == float('inf'):
            return None

        # 重建路径
        path_ids = []
        current = end_spot_id
        while current is not None:
            path_ids.append(current)
            current = previous[current]
        path_ids.reverse()

        # 构建路径信息
        path_spots = [self._display_name(self.spots[spot_id]) for spot_id in path_ids]
        path_node_ids = [self.spots[spot_id].space_id for spot_id in path_ids]
        path_points = [self._spot_point(self.spots[spot_id]) for spot_id in path_ids]
        
        # 构建详细步骤
        steps = []
        for i in range(len(path_ids) - 1):
            from_spot = self.spots[path_ids[i]]
            to_spot = self.spots[path_ids[i + 1]]
            
            # 查找边的距离
            edge_distance = None
            for neighbor, dist in self.graph[path_ids[i]]:
                if neighbor == path_ids[i + 1]:
                    edge_distance = dist
                    break
            
            if edge_distance is not None:
                steps.append({
                    'from_id': from_spot.space_id,
                    'to_id': to_spot.space_id,
                    'from': self._display_name(from_spot),
                    'to': self._display_name(to_spot),
                    'distance': float(edge_distance),
                    'from_coords': self._spot_point(from_spot),
                    'to_coords': self._spot_point(to_spot),
                })

        return {
            'path': path_spots,
            'path_node_ids': path_node_ids,
            'path_points': path_points,
            'distance': round(distances[end_spot_id], 2),
            'steps': steps
        }

    def rebuild_graph(self):
        """重建图 — 当数据库中的连接关系改变时调用"""
        self._build_graph()


# 全局单例（可选，用于缓存）
_navigator_instance = None


def get_navigator() -> DijkstraNavigator:
    """
    获取导航器实例（单例模式）
    """
    global _navigator_instance
    if _navigator_instance is None:
        _navigator_instance = DijkstraNavigator()
    return _navigator_instance


def find_path(start_spot_id: int, end_spot_id: int) -> Optional[Dict]:
    """
    便利函数：计算两个停车位之间的最短路径
    
    Args:
        start_spot_id: 起点停车位 ID
        end_spot_id: 终点停车位 ID
        
    Returns:
        路径信息字典或 None
    """
    navigator = get_navigator()
    return navigator.find_shortest_path(start_spot_id, end_spot_id)


def find_path_by_spot_code(start_code: str, end_code: str) -> Optional[Dict]:
    """
    便利函数：通过停车位编号查找路径
    
    Args:
        start_code: 起点停车位编号（如 'A-01'）
        end_code: 终点停车位编号（如 'B-05'）
        
    Returns:
        路径信息字典或 None
    """
    try:
        start_spot = ParkingSpace.objects.get(space_id=start_code)
        end_spot = ParkingSpace.objects.get(space_id=end_code)
        return find_path(start_spot.id, end_spot.id)
    except ParkingSpace.DoesNotExist:
        return None
