from flask import Flask, request, jsonify
from .constants import DEFAULT_A, DEFAULT_K, DEFAULT_B, DEFAULT_NUM_SKUS, WALKABLE, SHELF
from .data_generator import generate_warehouse_map, generate_random_order, get_all_points_for_tsp
from .tsp_solver import shorted_round_trip, validate_route

app = Flask(__name__)

current_map_data = None
current_order = None


def initialize_map():
    global current_map_data, current_order
    current_map_data = generate_warehouse_map(DEFAULT_A, DEFAULT_K, DEFAULT_B)
    current_order = None


initialize_map()


@app.route('/api/map_info', methods=['GET'])
def get_map_info():
    if current_map_data is None:
        return jsonify({"success": False, "error": "地图未初始化"}), 500
    
    return jsonify({
        "success": True,
        "rows": current_map_data["rows"],
        "cols": current_map_data["cols"],
        "start": current_map_data["start"],
        "walkable_points": current_map_data["walkable_points"],
        "shelves": current_map_data["shelves"],
        "params": current_map_data["params"]
    })


@app.route('/api/generate_order', methods=['POST'])
def api_generate_order():
    global current_map_data, current_order
    
    data = request.get_json() or {}
    
    x = data.get('x', DEFAULT_A)
    k = data.get('k', DEFAULT_K)
    b = data.get('b', DEFAULT_B)
    num_skus = data.get('num_skus', DEFAULT_NUM_SKUS)
    
    current_map_data = generate_warehouse_map(x, k, b)
    current_order = generate_random_order(current_map_data, num_skus)
    
    return jsonify({
        "success": True,
        "order_id": current_order["order_id"],
        "map_params": current_map_data["params"],
        "order": current_order
    })


@app.route('/api/solve', methods=['POST'])
def api_solve():
    global current_map_data
    
    data = request.get_json()
    
    if current_map_data is None:
        return jsonify({"success": False, "error": "地图未初始化"}), 500
    
    start = data.get('start', current_map_data["start"])
    middle_points = data.get('middle_points', [])
    
    if not middle_points:
        return jsonify({
            "success": True,
            "route": [start],
            "total_distance": 0
        })
    
    result = shorted_round_trip(
        current_map_data["map"],
        start,
        middle_points
    )
    
    return jsonify({
        "success": True,
        "route": result["route"],
        "total_distance": result["total_distance"]
    })


@app.route('/api/validate_route', methods=['POST'])
def api_validate_route():
    global current_map_data, current_order
    
    data = request.get_json()
    
    if current_map_data is None:
        return jsonify({"valid": False, "error": "地图未初始化"}), 500
    
    route = data.get('route', [])
    order_skus = data.get('order_skus', [])
    
    if current_order and 'skus' in current_order:
        order_skus = [[sku["row"], sku["col"]] for sku in current_order["skus"]]
    
    result = validate_route(
        current_map_data["map"],
        route,
        order_skus
    )
    
    return jsonify(result)


@app.route('/api/current_order', methods=['GET'])
def get_current_order():
    global current_order
    
    if current_order is None:
        return jsonify({"success": False, "error": "无当前订单"}), 404
    
    return jsonify({
        "success": True,
        "order": current_order
    })


@app.route('/api/calculate_distance', methods=['POST'])
def api_calculate_distance():
    global current_map_data
    
    data = request.get_json()
    route = data.get('route', [])
    
    if current_map_data is None:
        return jsonify({"success": False, "error": "地图未初始化"}), 500
    
    from .shortest_path import calculate_route_distance
    distance = calculate_route_distance(current_map_data["map"], route)
    
    return jsonify({
        "success": True,
        "distance": distance if distance != float('inf') else None
    })


@app.route('/api/route_from_waypoints', methods=['POST'])
def api_route_from_waypoints():
    global current_map_data
    
    data = request.get_json()
    
    if current_map_data is None:
        return jsonify({"success": False, "error": "地图未初始化"}), 500
    
    waypoints = data.get('waypoints', [])
    return_to_start = data.get('return_to_start', True)
    
    if not waypoints:
        return jsonify({"success": False, "error": "需要指定路点序列"}), 400
    
    from .shortest_path import shortest_path_sequence, calculate_route_distance
    
    start = current_map_data["start"]
    all_points = [start] + waypoints
    if return_to_start:
        all_points.append(start)
    
    full_route = []
    total_distance = 0
    
    for i in range(len(all_points) - 1):
        segment = shortest_path_sequence(
            current_map_data["map"],
            all_points[i],
            all_points[i + 1]
        )
        
        if segment is None:
            return jsonify({
                "success": False,
                "error": f"无法从 {all_points[i]} 到达 {all_points[i+1]}"
            }), 400
        
        if i == 0:
            full_route.extend(segment)
        else:
            full_route.extend(segment[1:])
        
        total_distance += len(segment) - 1
    
    return jsonify({
        "success": True,
        "route": full_route,
        "total_distance": total_distance
    })


if __name__ == '__main__':
    app.run(debug=True)
