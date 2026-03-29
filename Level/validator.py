from collections import deque


def find_first_open_cell(grid) :
    for y, row in enumerate(grid) :
        for x, cell in enumerate(row) :
            if not cell :
                return x, y

    return None


def has_connected_open_area(grid) :
    # 空地必须只有一个连通区域，否则说明存在孔洞或分离区域。
    start = find_first_open_cell(grid)
    if start is None :
        return False

    visited = {start}
    queue = deque([start])

    while queue :
        x, y = queue.popleft()

        for offset_x, offset_y in ((1, 0), (-1, 0), (0, 1), (0, -1)) :
            neighbor_x = x + offset_x
            neighbor_y = y + offset_y
            is_out_of_bounds = (
                neighbor_x < 0 or
                neighbor_y < 0 or
                neighbor_y >= len(grid) or
                neighbor_x >= len(grid[neighbor_y])
            )

            if is_out_of_bounds or grid[neighbor_y][neighbor_x] :
                continue

            neighbor = (neighbor_x, neighbor_y)
            if neighbor in visited :
                continue

            visited.add(neighbor)
            queue.append(neighbor)

    open_cell_count = 0
    for row in grid :
        for cell in row :
            if not cell :
                open_cell_count += 1

    return len(visited) == open_cell_count


def validate(level) :
    grid = level["grid"]
    if not grid :
        return False

    # 要求所有行长度一致，保证 grid 是规则二维数组。
    cols = len(grid[0])
    for row in grid :
        if len(row) != cols :
            return False

    return has_connected_open_area(grid)
