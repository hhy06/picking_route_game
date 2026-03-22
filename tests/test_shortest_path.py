import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.shortest_path import shortest_path_sequence, distance_between_points, calculate_route_distance
from backend.constants import WALKABLE, SHELF


def test_shortest_path_same_point():
    grid = [[WALKABLE, WALKABLE], [WALKABLE, WALKABLE]]
    result = shortest_path_sequence(grid, [0, 0], [0, 0])
    assert result == [[0, 0], [0, 0]]
    print("test_shortest_path_same_point PASSED")


def test_shortest_path_simple():
    grid = [
        [WALKABLE, WALKABLE, WALKABLE],
        [WALKABLE, SHELF, WALKABLE],
        [WALKABLE, WALKABLE, WALKABLE]
    ]
    result = shortest_path_sequence(grid, [0, 0], [2, 2])
    assert result is not None
    assert result[0] == [0, 0]
    assert result[-1] == [2, 2]
    print("test_shortest_path_simple PASSED")


def test_shortest_path_no_path():
    grid = [
        [WALKABLE, SHELF, WALKABLE],
        [SHELF, SHELF, SHELF],
        [WALKABLE, SHELF, WALKABLE]
    ]
    result = shortest_path_sequence(grid, [0, 0], [2, 2])
    assert result is None
    print("test_shortest_path_no_path PASSED")


def test_distance_between_points():
    grid = [
        [WALKABLE, WALKABLE, WALKABLE],
        [WALKABLE, WALKABLE, WALKABLE],
        [WALKABLE, WALKABLE, WALKABLE]
    ]
    dist = distance_between_points(grid, [0, 0], [0, 2])
    assert dist == 2
    print("test_distance_between_points PASSED")


def test_calculate_route_distance():
    grid = [
        [WALKABLE, WALKABLE, WALKABLE],
        [WALKABLE, WALKABLE, WALKABLE],
        [WALKABLE, WALKABLE, WALKABLE]
    ]
    route = [[0, 0], [0, 1], [0, 2], [2, 2]]
    dist = calculate_route_distance(grid, route)
    assert dist == 4
    print("test_calculate_route_distance PASSED")


def test_shortest_path_horizontal():
    grid = [[WALKABLE] * 5 for _ in range(1)]
    result = shortest_path_sequence(grid, [0, 0], [0, 4])
    assert result == [[0, 0], [0, 1], [0, 2], [0, 3], [0, 4]]
    print("test_shortest_path_horizontal PASSED")


def test_shortest_path_vertical():
    grid = [[WALKABLE] for _ in range(5)]
    result = shortest_path_sequence(grid, [0, 0], [4, 0])
    assert result == [[0, 0], [1, 0], [2, 0], [3, 0], [4, 0]]
    print("test_shortest_path_vertical PASSED")


if __name__ == "__main__":
    test_shortest_path_same_point()
    test_shortest_path_simple()
    test_shortest_path_no_path()
    test_distance_between_points()
    test_calculate_route_distance()
    test_shortest_path_horizontal()
    test_shortest_path_vertical()
    print("\nAll shortest_path tests PASSED!")
