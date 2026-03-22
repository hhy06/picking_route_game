import random
import uuid
from .constants import WALKABLE, SHELF, DEFAULT_A, DEFAULT_K, DEFAULT_B, DEFAULT_NUM_SKUS, DIRECTIONS


def generate_warehouse_map(a=None, k=None, b=None):
    a = a if a is not None else DEFAULT_A
    k = k if k is not None else DEFAULT_K
    b = b if b is not None else DEFAULT_B
    
    rows = 2 * a + 1
    cols = k * (b + 1) + 1
    
    grid = []
    walkable_points = []
    shelves = []
    
    for r in range(rows):
        row = []
        for c in range(cols):
            is_walkable_row = (r % 2 == 0)
            is_walkable_col = (c % (b + 1) == 0)
            
            if is_walkable_row or is_walkable_col:
                row.append(WALKABLE)
                walkable_points.append([r, c])
            else:
                row.append(SHELF)
                shelves.append([r, c])
        
        grid.append(row)
    
    start = [rows - 1, 0]
    
    return {
        "map": grid,
        "rows": rows,
        "cols": cols,
        "start": start,
        "walkable_points": walkable_points,
        "shelves": shelves,
        "params": {"a": a, "k": k, "b": b}
    }


def get_adjacent_walkable_points(map_data):
    shelves = map_data["shelves"]
    walkable = set(tuple(p) for p in map_data["walkable_points"])
    grid = map_data["map"]
    
    pickup_points = []
    
    for shelf_r, shelf_c in shelves:
        for dr, dc in DIRECTIONS:
            adj_r, adj_c = shelf_r + dr, shelf_c + dc
            if (0 <= adj_r < map_data["rows"] and 
                0 <= adj_c < map_data["cols"] and
                (adj_r, adj_c) in walkable):
                pickup_points.append([adj_r, adj_c])
    
    unique_pickup = []
    seen = set()
    for p in pickup_points:
        if tuple(p) not in seen:
            seen.add(tuple(p))
            unique_pickup.append(p)
    
    return unique_pickup


def get_shelf_locations(map_data):
    return map_data["shelves"]


def generate_random_order(map_data, num_skus=None):
    num_skus = num_skus if num_skus is not None else DEFAULT_NUM_SKUS
    
    pickup_points = get_adjacent_walkable_points(map_data)
    
    if len(pickup_points) < num_skus:
        num_skus = len(pickup_points)
    
    selected = random.sample(pickup_points, num_skus)
    
    skus = []
    for i, point in enumerate(selected):
        skus.append({
            "sku_id": f"S{i+1}",
            "row": point[0],
            "col": point[1],
            "label": f"B{i+1}"
        })
    
    order_id = f"order_{uuid.uuid4().hex[:8]}"
    
    return {
        "order_id": order_id,
        "skus": skus
    }


def get_all_points_for_tsp(map_data, order_skus):
    start = map_data["start"]
    middle_points = [[sku["row"], sku["col"]] for sku in order_skus]
    return start, middle_points
