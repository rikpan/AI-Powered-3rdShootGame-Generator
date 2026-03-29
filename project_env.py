import os
from pathlib import Path


def load_local_env(start_dir = None, *, override = False) :
    # 从当前目录向上查找 .env，让各模块都能独立运行时复用同一份配置。
    base_dir = Path(start_dir or Path.cwd()).resolve()

    for directory in (base_dir, *base_dir.parents) :
        env_path = directory / ".env"
        if not env_path.exists() :
            continue

        with env_path.open("r", encoding = "utf-8") as env_file :
            for raw_line in env_file :
                line = raw_line.strip()
                if not line or line.startswith("#") or "=" not in line :
                    continue

                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")

                if not key or not value :
                    continue

                if override or key not in os.environ :
                    os.environ[key] = value

        return env_path

    return None
