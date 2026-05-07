"""Navigation connectivity tests"""
from django.test import TestCase
from parking.models import ParkingSpace
from parking.navigation import RoadNavigator, find_path


class NavigationConnectivityTest(TestCase):
    """Test that all parking spots can reach each other via road network."""

    def setUp(self):
        self.nav = RoadNavigator()

    def test_graph_stats(self):
        print(f'\n总节点数: {len(self.nav.graph)}')
        print(f'总车位数: {len(self.nav.spots)}')
        for floor in ('B2', 'B1', '1F'):
            road_count = len(self.nav.road_nodes.get(floor, []))
            spot_count = len(self.nav.spots_by_floor.get(floor, {}))
            print(f'{floor}: {road_count} 道路节点, {spot_count} 车位')

    def _bfs_reachable(self, graph, start):
        visited = set()
        queue = [start]
        visited.add(start)
        while queue:
            node = queue.pop(0)
            for neighbor, _ in graph.get(node, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        return visited

    def test_full_connectivity(self):
        """All nodes should be reachable from any starting node."""
        all_nodes = set(self.nav.graph.keys())
        start = list(all_nodes)[0]
        reachable = self._bfs_reachable(self.nav.graph, start)
        print(f'\n连通性: {len(reachable)}/{len(all_nodes)} 节点可达')
        self.assertEqual(len(reachable), len(all_nodes),
                         f"Only {len(reachable)}/{len(all_nodes)} nodes reachable. "
                         f"Unreachable: {all_nodes - reachable}")

    def test_cross_floor_paths(self):
        """Cross-floor paths must work via elevator connections."""
        for floor1 in ('B2', 'B1', '1F'):
            for floor2 in ('B2', 'B1', '1F'):
                if floor1 == floor2:
                    continue
                spots_f1 = list(self.nav.spots_by_floor.get(floor1, {}).keys())
                spots_f2 = list(self.nav.spots_by_floor.get(floor2, {}).keys())
                if spots_f1 and spots_f2:
                    result = find_path(spots_f1[0], spots_f2[0])
                    self.assertIsNotNone(result,
                                         f"No path from {floor1}#{spots_f1[0]} to {floor2}#{spots_f2[0]}")
                    self.assertGreater(result['distance'], 0)

    def test_same_floor_paths(self):
        """Same-floor paths must work."""
        for floor in ('B2', 'B1', '1F'):
            spots = list(self.nav.spots_by_floor.get(floor, {}).keys())
            if len(spots) >= 2:
                result = find_path(spots[0], spots[1])
                self.assertIsNotNone(result, f"No path within {floor}")

    def test_sample_reachability(self):
        """Sample pairwise reachability across all floors."""
        spot_ids = list(self.nav.spots.keys())
        unreachable = 0
        total = 0
        for i in range(0, len(spot_ids), 5):
            for j in range(i+1, min(i+6, len(spot_ids))):
                total += 1
                result = find_path(spot_ids[i], spot_ids[j])
                if result is None:
                    unreachable += 1
        print(f'\n抽样可达性: {total} 对, {unreachable} 对不可达')
        self.assertEqual(unreachable, 0, f"{unreachable}/{total} pairs unreachable")
