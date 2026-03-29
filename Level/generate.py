import argparse
import random
import sys
from dataclasses import dataclass

from validator import validate


@dataclass(frozen = True)
class level_generator_profile :
    name : str
    grid_width : int
    grid_height : int
    border_size : int
    wall_probability : float
    simulation_steps : int
    neighbor_threshold : int
    max_attempts : int


# 当前这套“随机初始 + 元胞自动机平滑 + 最终封边”的方案命名为“平坦随机”。
flat_random_profile = level_generator_profile(
    name = "平坦随机",
    grid_width = 30,
    grid_height = 30,
    border_size = 10,
    wall_probability = 0.5,
    simulation_steps = 2,
    neighbor_threshold = 5,
    max_attempts = 50,
)


def final_grid_width(profile) :
    return profile.grid_width + profile.border_size * 2


def final_grid_height(profile) :
    return profile.grid_height + profile.border_size * 2


def create_initial_grid(rng, profile) :
    # 先生成内部区域，边界稍后再统一补上。
    grid = []

    for _ in range(profile.grid_height) :
        row = []

        for _ in range(profile.grid_width) :
            row.append(rng.random() < profile.wall_probability)

        grid.append(row)

    return grid


def count_wall_neighbors(grid, x, y, profile) :
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
                neighbor_x >= profile.grid_width or
                neighbor_y >= profile.grid_height
            )

            if is_out_of_bounds or grid[neighbor_y][neighbor_x] :
                wall_count += 1

    return wall_count


def run_cellular_automata(grid, profile) :
    # 按元胞自动机规则生成下一轮地图。
    next_grid = []

    for y in range(profile.grid_height) :
        next_row = []

        for x in range(profile.grid_width) :
            wall_count = count_wall_neighbors(grid, x, y, profile)
            next_row.append(wall_count >= profile.neighbor_threshold)

        next_grid.append(next_row)

    return next_grid


def apply_border_walls(grid, profile) :
    # 在地图生成完成后统一填充边界，强保证外围一定是墙。
    bordered_grid = []

    for y in range(final_grid_height(profile)) :
        bordered_row = []

        for x in range(final_grid_width(profile)) :
            is_border = (
                x < profile.border_size or
                y < profile.border_size or
                x >= final_grid_width(profile) - profile.border_size or
                y >= final_grid_height(profile) - profile.border_size
            )

            if is_border :
                bordered_row.append(True)
                continue

            inner_x = x - profile.border_size
            inner_y = y - profile.border_size
            bordered_row.append(grid[inner_y][inner_x])

        bordered_grid.append(bordered_row)

    return bordered_grid


def build_level(level_no = 1, seed = None, profile = flat_random_profile) :
    # 先随机初始化，再多轮平滑，最后统一封边。
    rng = random.Random(seed)
    grid = create_initial_grid(rng, profile)

    for _ in range(profile.simulation_steps) :
        grid = run_cellular_automata(grid, profile)

    grid = apply_border_walls(grid, profile)

    return {
        "level_no" : level_no,
        "grid" : grid,
    }


def generate_level(level_no = 1, seed = None, profile = flat_random_profile) :
    # 如果出现孔洞或分离区域，就继续尝试下一张地图。
    seed_rng = random.Random(seed)

    for _ in range(profile.max_attempts) :
        current_seed = None if seed is None else seed_rng.randrange(0, 2**31)
        level = build_level(level_no = level_no, seed = current_seed, profile = profile)

        if validate(level) :
            return level

    raise RuntimeError(f"failed to generate a valid connected level with profile: {profile.name}")


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
    level = generate_level(level_no = args.level_no, seed = args.seed, profile = flat_random_profile)
    print(f"生成方式 : {flat_random_profile.name}")
    print(render_grid(level["grid"]))


if __name__ == "__main__" :
    main()
