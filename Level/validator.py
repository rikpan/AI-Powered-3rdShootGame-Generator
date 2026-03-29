def validate(level):
    grid = level["grid"]
    rows = len(grid)
    cols = len(grid[0])

    # 1. 检查尺寸一致
    for row in grid:
        if len(row) != cols:
            return False

    # 2. 检查是否有初始三连（简单规则）
    for i in range(rows):
        for j in range(cols - 2):
            if grid[i][j] == grid[i][j+1] == grid[i][j+2]:
                return False

    return True