import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.shortest_path import shortest_path_sequence, distance_between_points
from backend.data_generator import generate_warehouse_map, generate_random_order
from backend.constants import WALKABLE


def test_build_distance_matrix():
    from backend.tsp_solver import build_distance_matrix
    
    grid = [
        [WALKABLE, WALKABLE, WALKABLE],
        [WALKABLE, WALKABLE, WALKABLE],
        [WALKABLE, WALKABLE, WALKABLE]
    ]
    points = [[0, 0], [0, 2], [2, 0]]
    
    matrix = build_distance_matrix(grid, points)
    
    assert len(matrix) == 3
    assert len(matrix[0]) == 3
    assert matrix[0][0] == 0
    assert matrix[0][1] == 2
    assert matrix[0][2] == 2
    print("test_build_distance_matrix PASSED")


def test_shorted_round_trip_empty_middle_points():
    from backend.tsp_solver import shorted_round_trip
    
    grid = [[WALKABLE, WALKABLE], [WALKABLE, WALKABLE]]
    result = shorted_round_trip(grid, [0, 0], [])
    
    assert result["route"] == [[0, 0]]
    assert result["total_distance"] == 0
    print("test_shorted_round_trip_empty_middle_points PASSED")


def test_shorted_round_trip_single_point():
    from backend.tsp_solver import shorted_round_trip
    
    grid = [[WALKABLE, WALKABLE], [WALKABLE, WALKABLE]]
    result = shorted_round_trip(grid, [0, 0], [[1, 1]])
    
    assert len(result["route"]) > 2
    assert result["route"][0] == [0, 0]
    assert result["route"][-1] == [0, 0]
    assert result["total_distance"] > 0
    print("test_shorted_round_trip_single_point PASSED")


def test_shorted_round_trip_multiple_points():
    from backend.tsp_solver import shorted_round_trip
    
    grid = [
        [WALKABLE, WALKABLE, WALKABLE, WALKABLE],
        [WALKABLE, WALKABLE, WALKABLE, WALKABLE],
        [WALKABLE, WALKABLE, WALKABLE, WALKABLE],
        [WALKABLE, WALKABLE, WALKABLE, WALKABLE]
    ]
    middle_points = [[0, 1], [0, 3], [2, 1]]
    result = shorted_round_trip(grid, [3, 0], middle_points)
    
    assert result["route"][0] == [3, 0]
    assert result["route"][-1] == [3, 0]
    assert result["total_distance"] > 0
    print("test_shorted_round_trip_multiple_points PASSED")


def test_shorted_round_trip_warehouse():
    from backend.tsp_solver import shorted_round_trip
    
    map_data = generate_warehouse_map(2, 3, 2)
    order = generate_random_order(map_data, 3)
    
    start = map_data["start"]
    middle_points = [[sku["row"], sku["col"]] for sku in order["skus"]]
    
    result = shorted_round_trip(map_data["map"], start, middle_points)
    
    assert result["route"][0] == start
    assert result["route"][-1] == start
    assert result["total_distance"] > 0
    print("test_shorted_round_trip_warehouse PASSED")


def test_validate_route_valid():
    from backend.tsp_solver import validate_route
    
    grid = [
        [WALKABLE, WALKABLE, WALKABLE],
        [WALKABLE, WALKABLE, WALKABLE],
        [WALKABLE, WALKABLE, WALKABLE]
    ]
    
    route = [[0, 0], [0, 1], [0, 2], [2, 2], [2, 0], [0, 0]]
    order_skus = [[0, 1], [0, 2], [2, 2]]
    
    result = validate_route(grid, route, order_skus)
    
    assert result["valid"] == True
    assert "total_distance" in result
    print("test_validate_route_valid PASSED")


def test_validate_route_missing_sku():
    from backend.tsp_solver import validate_route
    
    grid = [
        [WALKABLE, WALKABLE, WALKABLE],
        [WALKABLE, WALKABLE, WALKABLE],
        [WALKABLE, WALKABLE, WALKABLE]
    ]
    
    route = [[0, 0], [0, 1], [0, 0]]
    order_skus = [[0, 1], [0, 2], [2, 2]]
    
    result = validate_route(grid, route, order_skus)
    
    assert result["valid"] == False
    assert "error" in result
    print("test_validate_route_missing_sku PASSED")


def test_validate_route_no_return():
    from backend.tsp_solver import validate_route
    
    grid = [
        [WALKABLE, WALKABLE, WALKABLE],
        [WALKABLE, WALKABLE, WALKABLE],
        [WALKABLE, WALKABLE, WALKABLE]
    ]
    
    route = [[0, 0], [0, 1], [0, 2]]
    order_skus = [[0, 1], [0, 2]]
    
    result = validate_route(grid, route, order_skus)
    
    assert result["valid"] == False
    print("test_validate_route_no_return PASSED")


if __name__ == "__main__":
    test_build_distance_matrix()
    test_shorted_round_trip_empty_middle_points()
    test_shorted_round_trip_single_point()
    test_shorted_round_trip_multiple_points()
    test_shorted_round_trip_warehouse()
    test_validate_route_valid()
    test_validate_route_missing_sku()
    test_validate_route_no_return()
    print("\nAll tsp_solver tests PASSED!")
