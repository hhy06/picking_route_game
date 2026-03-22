# 算法规格文档

## 算法A: 最短路径 (shortest_path.py)

### 函数签名
```python
def shortest_path_sequence(grid_map, start_coord, end_coord):
    """
    在网格地图上求两点间最短路径
    
    参数:
        grid_map: 2D list, 0表示可通行空格, 1表示货架
        start_coord: [row, col] 起点坐标
        end_coord: [row, col] 终点坐标
    
    返回:
        list of [row, col] 连续格点序列，包含起点和终点
        如果无路径返回None
    """
```

### 示例
```python
grid_map = [
    [0, 1, 0],
    [0, 1, 0],
    [0, 0, 0]
]
start = [0, 0]
end = [2, 2]
result = shortest_path_sequence(grid_map, start, end)
# [[0,0], [1,0], [2,0], [2,1], [2,2]]
```

### 实现要求
- 使用BFS(广度优先搜索)
- 4方向移动(上下左右)
- 返回最短路径(格点数最少)

---

## 算法B: TSP回路求解 (tsp_solver.py)

### 函数签名
```python
def shorted_round_trip(grid_map, start_coord, middle_points_list):
    """
    求经过所有中间点一次的回路
    
    参数:
        grid_map: 2D list, 0表示可通行空格, 1表示货架
        start_coord: [row, col] 起点坐标
        middle_points_list: list of [row, col] 中间点列表
    
    返回:
        dict: {
            "route": [[r,c], ...],  # 完整回路坐标序列
            "total_distance": int   # 总步数
        }
    """
```

### 示例
```python
grid_map = [
    [0, 1, 0, 1, 0],
    [0, 1, 0, 1, 0],
    [0, 0, 0, 0, 0]
]
start = [2, 0]
middle_points = [[0, 2], [0, 4]]
result = shorted_round_trip(grid_map, start, middle_points)
# {
#     "route": [[2,0], [1,0], [0,0], [0,1], [0,2], ...],
#     "total_distance": 12
# }
```

### 实现步骤
1. 计算所有点对之间的最短路径距离(使用算法A)
2. 构建完全图距离矩阵
3. 使用elkai求解TSP得到最优访问顺序
4. 按最优顺序拼接路径

---

## 数据生成器 (data_generator.py)

### generate_warehouse_map
```python
def generate_warehouse_map(a, k, b):
    """
    生成仓库地图
    
    参数:
        a: 行参数, 实际行数=2a+1
        k: 每行货架段数
        b: 每段货架格子数
    
    返回:
        dict: {
            "map": [[0,1,...], ...],  # 2D grid
            "rows": int,
            "cols": int,
            "start": [row, col],
            "walkable_points": [[r,c], ...],
            "shelves": [[r,c], ...]
        }
    """
```

### generate_random_order
```python
def generate_random_order(map_data, num_skus):
    """
    从地图中随机生成订单
    
    参数:
        map_data: generate_warehouse_map返回的地图数据
        num_skus: SKU数量
    
    返回:
        dict: {
            "order_id": str,
            "skus": [{"sku_id": str, "row": int, "col": int, "label": str}, ...]
        }
    """
```

### 地图生成规则
```
行数: 2a+1 (奇数)
列数: k*(b+1)+1

可通行点(0):
  - 行坐标为偶数: 整行可通行
  - 列坐标 col % (b+1) == 0: 纵向走廊

不可通行点(1/货架):
  - 行坐标为奇数 且 列坐标 col % (b+1) != 0

起点: (2a, 0) 左下角第一个空格点
```

---

## 辅助函数

### distance_between_points
```python
def distance_between_points(grid_map, p1, p2):
    """计算两点间最短路径长度(步数)"""
```

### calculate_route_distance
```python
def calculate_route_distance(grid_map, route):
    """计算整条路线的总步数"""
```

### validate_route
```python
def validate_route(grid_map, route, order_skus):
    """验证路线是否有效(访问所有SKU且路径合法)"""
```
