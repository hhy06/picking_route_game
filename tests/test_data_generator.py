import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.data_generator import generate_warehouse_map, generate_random_order, get_all_points_for_tsp, get_adjacent_walkable_points
from backend.constants import WALKABLE, SHELF


def test_generate_warehouse_map_default():
    map_data = generate_warehouse_map(3, 4, 3)
    
    assert map_data["rows"] == 7
    assert map_data["cols"] == 17
    assert map_data["start"] == [6, 0]
    assert map_data["params"] == {"a": 3, "k": 4, "b": 3}
    
    assert len(map_data["walkable_points"]) > 0
    assert len(map_data["shelves"]) > 0
    print("test_generate_warehouse_map_default PASSED")


def test_generate_warehouse_map_small():
    map_data = generate_warehouse_map(1, 2, 2)
    
    assert map_data["rows"] == 3
    assert map_data["cols"] == 7
    
    grid = map_data["map"]
    for r in range(3):
        for c in range(7):
            is_walkable_row = (r % 2 == 0)
            is_walkable_col = (c % 3 == 0)
            if is_walkable_row or is_walkable_col:
                assert grid[r][c] == WALKABLE, f"({r},{c}) should be walkable"
            else:
                assert grid[r][c] == SHELF, f"({r},{c}) should be shelf"
    print("test_generate_warehouse_map_small PASSED")


def test_generate_random_order():
    map_data = generate_warehouse_map(3, 4, 3)
    order = generate_random_order(map_data, 5)
    
    assert "order_id" in order
    assert len(order["skus"]) == 5
    
    for sku in order["skus"]:
        assert "sku_id" in sku
        assert "row" in sku
        assert "col" in sku
        assert "label" in sku
        
        assert map_data["map"][sku["row"]][sku["col"]] == WALKABLE
    print("test_generate_random_order PASSED")


def test_generate_random_order_more_skus_than_pickup():
    map_data = generate_warehouse_map(1, 2, 1)
    pickup_points = get_adjacent_walkable_points(map_data)
    order = generate_random_order(map_data, 100)
    
    assert len(order["skus"]) <= len(pickup_points)
    print("test_generate_random_order_more_skus_than_pickup PASSED")


def test_get_all_points_for_tsp():
    map_data = generate_warehouse_map(2, 3, 2)
    order = generate_random_order(map_data, 4)
    
    start, middle_points = get_all_points_for_tsp(map_data, order["skus"])
    
    assert start == map_data["start"]
    assert len(middle_points) == 4
    
    for mp in middle_points:
        assert len(mp) == 2
    print("test_get_all_points_for_tsp PASSED")


def test_walkable_points_include_start():
    map_data = generate_warehouse_map(2, 3, 2)
    start = map_data["start"]
    
    assert start in map_data["walkable_points"]
    print("test_walkable_points_include_start PASSED")


def test_pickup_points_are_walkable():
    map_data = generate_warehouse_map(2, 3, 2)
    pickup_points = get_adjacent_walkable_points(map_data)
    
    for pt in pickup_points:
        r, c = pt[0], pt[1]
        assert map_data["map"][r][c] == WALKABLE
    print("test_pickup_points_are_walkable PASSED")


def test_pickup_points_adjacent_to_shelves():
    map_data = generate_warehouse_map(2, 3, 2)
    pickup_points = get_adjacent_walkable_points(map_data)
    shelves = map_data["shelves"]
    
    shelves_set = set(tuple(s) for s in shelves)
    
    for pt in pickup_points:
        r, c = pt[0], pt[1]
        adjacent_to_shelf = False
        for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
            if (r+dr, c+dc) in shelves_set:
                adjacent_to_shelf = True
                break
        assert adjacent_to_shelf, f"Point {pt} is not adjacent to any shelf"
    print("test_pickup_points_adjacent_to_shelves PASSED")


if __name__ == "__main__":
    test_generate_warehouse_map_default()
    test_generate_warehouse_map_small()
    test_generate_random_order()
    test_generate_random_order_more_skus_than_pickup()
    test_get_all_points_for_tsp()
    test_walkable_points_include_start()
    test_pickup_points_are_walkable()
    test_pickup_points_adjacent_to_shelves()
    print("\nAll data_generator tests PASSED!")
