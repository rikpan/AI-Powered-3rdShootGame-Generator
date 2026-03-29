import argparse
import random
import sys

from validator import validate


# 这里的宽高只表示内部可生成区域，不包含外围边界。
grid_width = 30
grid_height = 30
border_size = 10
wall_probability = 0.5
simulation_steps = 2
neighbor_threshold = 5
max_attempts = 50


def final_grid_width() :
    return grid_width + border_size * 2


def final_grid_height() :
    return grid_height + border_size * 2


def create_initial_grid(rng) :
    # 先生成内部区域，边界稍后再统一补上。
    grid = []

    for _ in range(grid_height) :
        row = []

        for _ in range(grid_width) :
            row.append(rng.random() < wall_probability)

        grid.append(row)

    return grid


def count_wall_neighbors(grid, x, y) :
    # 统计八邻域中的墙体数量，越靠近密集区域越容易在后续迭代中变成墙。
    wall_count = 0

    for offset_y in range(-1, 2) :
        for offset_x in range(-1, 2) :
            if offset_x == 0 and offset_y == 0 :
                continue

            neighbor_x = x + offset_x
            neighbor_y = y + offset_y
            is_out_of_bounds = (
                neighbor_x < 0 or
                neighbor_y < 0 or
                neighbor_x >= grid_width or
                neighbor_y >= grid_height
            )

            if is_out_of_bounds or grid[neighbor_y][neighbor_x] :
                wall_count += 1

    return wall_count


def run_cellular_automata(grid) :
    # 按元胞自动机规则生成下一轮地图。
    next_grid = []

    for y in range(grid_height) :
        next_row = []

        for x in range(grid_width) :
            wall_count = count_wall_neighbors(grid, x, y)
            next_row.append(wall_count >= neighbor_threshold)

        next_grid.append(next_row)

    return next_grid


def apply_border_walls(grid) :
    # 在地图生成完成后统一填充边界，强保证外围一定是墙。
    bordered_grid = []

    for y in range(final_grid_height()) :
        bordered_row = []

        for x in range(final_grid_width()) :
            is_border = (
                x < border_size or
                y < border_size or
                x >= final_grid_width() - border_size or
                y >= final_grid_height() - border_size
            )

            if is_border :
                bordered_row.append(True)
                continue

            inner_x = x - border_size
            inner_y = y - border_size
            bordered_row.append(grid[inner_y][inner_x])

        bordered_grid.append(bordered_row)

    return bordered_grid


def build_level(level_no = 1, seed = None) :
    # 先随机初始化，再多轮平滑，最后统一封边。
    rng = random.Random(seed)
    grid = create_initial_grid(rng)

    for _ in range(simulation_steps) :
        grid = run_cellular_automata(grid)

    grid = apply_border_walls(grid)

    return {
        "level_no" : level_no,
        "grid" : grid,
    }


def generate_level(level_no = 1, seed = None) :
    # 如果出现孔洞或分离区域，就继续尝试下一张地图。
    seed_rng = random.Random(seed)

    for _ in range(max_attempts) :
        current_seed = None if seed is None else seed_rng.randrange(0, 2**31)
        level = build_level(level_no = level_no, seed = current_seed)

        if validate(level) :
            return level

    print("failed to generate a valid connected level")
    return level


def render_grid(grid) :
    rendered_rows = []

    for row in grid :
        rendered_rows.append("".join("• " if cell else "  " for cell in row))

    return "\n".join(rendered_rows)


def parse_args() :
    parser = argparse.ArgumentParser(description = "使用元胞自动机生成关卡地图")
    parser.add_argument("--level-no", type = int, default = 1, help = "关卡编号")
    parser.add_argument("--seed", type = int, default = None, help = "随机数种子")
    return parser.parse_args()


def main() :
    # 直接执行脚本时打印可视化地图。
    if hasattr(sys.stdout, "reconfigure") :
        sys.stdout.reconfigure(encoding = "utf-8")

    args = parse_args()
    level = generate_level(level_no = args.level_no, seed = args.seed)
    print(render_grid(level["grid"]))


if __name__ == "__main__" :
    main()
