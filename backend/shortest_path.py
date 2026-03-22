from collections import deque
from .constants import DIRECTIONS, WALKABLE


def shortest_path_sequence(grid_map, start_coord, end_coord):
    start = tuple(start_coord)
    end = tuple(end_coord)
    
    if start == end:
        return [start_coord, end_coord]
    
    rows = len(grid_map)
    cols = len(grid_map[0]) if rows > 0 else 0
    
    if not (0 <= start[0] < rows and 0 <= start[1] < cols):
        return None
    if not (0 <= end[0] < rows and 0 <= end[1] < cols):
        return None
    
    if grid_map[start[0]][start[1]] != WALKABLE:
        return None
    if grid_map[end[0]][end[1]] != WALKABLE:
        return None
    
    queue = deque([start])
    parent = {start: None}
    
    while queue:
        current = queue.popleft()
        
        if current == end:
            path = []
            node = end
            while node is not None:
                path.append(list(node))
                node = parent[node]
            return path[::-1]
        
        for dr, dc in DIRECTIONS:
            neighbor = (current[0] + dr, current[1] + dc)
            
            if (0 <= neighbor[0] < rows and 
                0 <= neighbor[1] < cols and
                grid_map[neighbor[0]][neighbor[1]] == WALKABLE and
                neighbor not in parent):
                
                parent[neighbor] = current
                queue.append(neighbor)
    
    return None


def distance_between_points(grid_map, p1, p2):
    path = shortest_path_sequence(grid_map, p1, p2)
    if path is None:
        return float('inf')
    return len(path) - 1


def calculate_route_distance(grid_map, route):
    if not route or len(route) < 2:
        return 0
    
    total_distance = 0
    for i in range(len(route) - 1):
        dist = distance_between_points(grid_map, route[i], route[i+1])
        if dist == float('inf'):
            return float('inf')
        total_distance += dist
    
    return total_distance
