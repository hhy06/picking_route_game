# 项目结构文档

## 1. 目录结构

```
picking_route_game_website3/
├── backend/
│   ├── __init__.py
│   ├── app.py              # Flask服务器主文件
│   ├── shortest_path.py    # 算法A: BFS最短路径
│   ├── tsp_solver.py       # 算法B: TSP回路求解
│   ├── data_generator.py   # 地图和订单生成器
│   └── constants.py        # 全局常量定义
├── tests/
│   ├── __init__.py
│   ├── test_shortest_path.py
│   ├── test_tsp_solver.py
│   └── test_data_generator.py
├── frontend/               # 暂不实现(Vue3)
├── docs/                   # 文档
├── start.py                # 启动脚本
├── requirements.txt        # Python依赖
└── 000.human_plan.txt     # 原始需求文档
```

## 2. 文件功能说明

### backend/constants.py
- 定义地图参数常量
- 定义方向向量
- 定义颜色常量(用于前端)

### backend/shortest_path.py
- `shortest_path_sequence(grid_map, start_coord, end_coord) -> list`
- BFS算法求两点间最短路径

### backend/tsp_solver.py
- `shorted_round_trip(grid_map, start_coord, middle_points_list) -> dict`
- 构建完全图 + elkai求解TSP

### backend/data_generator.py
- `generate_warehouse_map(a, k, b) -> dict` - 生成仓库地图
- `generate_random_order(map_data, num_skus) -> dict` - 生成随机订单
- `get_walkable_points(map_data) -> list` - 获取所有可通行点

### backend/app.py
- Flask应用
- RESTful API端点

## 3. 程序运行流程

```
start.py
  └─> app.py (Flask)
        ├─> /api/map_info     - 获取地图信息
        ├─> /api/generate_order - 生成订单
        ├─> /api/solve        - AI求解
        └─> /api/validate_route - 验证人类路线
```

## 4. API接口详细规格

### GET /api/map_info
获取当前地图信息

Response:
```json
{
  "success": true,
  "rows": 7,
  "cols": 13,
  "start": [6, 0],
  "walkable_points": [[0,0], [0,4], [2,0], ...],
  "shelves": [[1,1], [1,2], [1,3], ...]
}
```

### POST /api/generate_order
生成随机订单

Request:
```json
{
  "a": 3,
  "k": 4,
  "b": 3,
  "num_skus": 5
}
```

Response:
```json
{
  "success": true,
  "order_id": "order_20240322_001",
  "map_params": {"a": 3, "k": 4, "b": 3},
  "order": {
    "skus": [
      {"sku_id": "S1", "row": 1, "col": 5, "label": "B1"},
      {"sku_id": "S2", "row": 3, "col": 9, "label": "B2"},
      ...
    ]
  }
}
```

### POST /api/solve
求解TSP

Request:
```json
{
  "start": [6, 0],
  "middle_points": [[1, 5], [3, 9], [5, 1]]
}
```

Response:
```json
{
  "success": true,
  "route": [[6,0], [4,0], [2,0], [1,0], [1,5], ...],
  "total_distance": 25
}
```

### POST /api/validate_route
验证人类路线

Request:
```json
{
  "route": [[6,0], [1,5], [3,9], [5,1], [6,0]],
  "order_skus": [[1,5], [3,9], [5,1]]
}
```

Response:
```json
{
  "valid": true,
  "total_distance": 28,
  "message": "路线有效"
}
```
或
```json
{
  "valid": false,
  "error": "路线未访问所有SKU点"
}
```

## 5. 依赖关系

```
start.py
  └─> backend/app.py
        ├─> backend/constants.py
        ├─> backend/shortest_path.py
        ├─> backend/tsp_solver.py
        └─> backend/data_generator.py
```

## 6. 数据流

1. 服务器启动时生成默认地图
2. 用户请求生成订单 -> 从货架点中随机选取
3. 用户提交路线 -> 验证并计算距离
4. 用户请求AI求解 -> elkai计算最优TSP回路
