from .shortest_path import shortest_path_sequence, distance_between_points


def build_distance_matrix(grid_map, all_points):
    n = len(all_points)
    matrix = [[0] * n for _ in range(n)]
    
    for i in range(n):
        for j in range(i + 1, n):
            dist = distance_between_points(grid_map, all_points[i], all_points[j])
            matrix[i][j] = dist
            matrix[j][i] = dist
    
    return matrix


def solve_tsp_with_elkai(distance_matrix):
    try:
        import elkai
        tour = elkai.solve_int_matrix(distance_matrix)
        return tour
    except ImportError:
        raise ImportError("elkai library is required. Install with: pip install elkai")


def shorted_round_trip(grid_map, start_coord, middle_points_list):
    if not middle_points_list:
        return {
            "route": [start_coord],
            "total_distance": 0
        }
    
    all_points = [start_coord] + middle_points_list
    n = len(all_points)
    
    if n == 2:
        path = shortest_path_sequence(grid_map, start_coord, middle_points_list[0])
        return {
            "route": path + path[-2::-1] if path else [start_coord],
            "total_distance": (len(path) - 1) * 2 if path else 0
        }
    
    distance_matrix = build_distance_matrix(grid_map, all_points)
    
    tour = solve_tsp_with_elkai(distance_matrix)
    
    if tour[0] != 0:
        idx = tour.index(0)
        tour = tour[idx:] + tour[:idx]
    
    full_route = []
    total_distance = 0
    
    for i in range(len(tour)):
        p1_idx = tour[i]
        p2_idx = tour[(i + 1) % len(tour)]
        
        segment_path = shortest_path_sequence(
            grid_map, 
            all_points[p1_idx], 
            all_points[p2_idx]
        )
        
        if i == 0:
            full_route.extend(segment_path)
        else:
            full_route.extend(segment_path[1:])
        
        total_distance += len(segment_path) - 1
    
    return {
        "route": full_route,
        "total_distance": total_distance
    }


def validate_route(grid_map, route, order_skus):
    if not route or len(route) < 2:
        return {
            "valid": False,
            "error": "路线为空或太短"
        }
    
    if route[0] != route[-1]:
        return {
            "valid": False,
            "error": "路线必须从起点出发并返回起点"
        }
    
    order_set = set(tuple(p) for p in order_skus)
    visited = set()
    
    for point in route[1:-1]:
        pt = tuple(point)
        if pt in order_set:
            visited.add(pt)
    
    if len(visited) != len(order_set):
        missing = order_set - visited
        return {
            "valid": False,
            "error": f"路线未访问所有SKU点，缺少 {len(missing)} 个点"
        }
    
    from .shortest_path import calculate_route_distance
    total_distance = calculate_route_distance(grid_map, route)
    
    if total_distance == float('inf'):
        return {
            "valid": False,
            "error": "路线包含无效路径"
        }
    
    return {
        "valid": True,
        "total_distance": total_distance,
        "message": "路线有效"
    }
