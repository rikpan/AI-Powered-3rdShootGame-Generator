import json
import os
from pathlib import Path
import sys
from openai import OpenAI
from validator import validate

current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from project_env import load_local_env

load_local_env(current_dir)

base_url = os.getenv("OPENAI_BASE_URL")
api_key = os.getenv("OPENAI_API_KEY")
if not base_url or not api_key:
    raise RuntimeError("请先在项目根目录 .env 中配置 OPENAI_BASE_URL 和 OPENAI_API_KEY")

client = OpenAI(
    base_url = base_url,
    api_key = api_key,
)

prompt = """
生成一个三消关卡，要求：
1. grid_size 为 6x6
2. 颜色只能是 red, blue, green
3. 输出必须是 JSON
4. grid 中不能出现初始三连

格式：
{
  "grid_size": [6,6],
  "colors": [...],
  "grid": [[...]],
  "moves": 20
}
"""

def generate_level():
    response = client.chat.completions.create(
        model = "gpt-4o-mini",
        messages = [{"role": "user", "content": prompt}],
        temperature = 0.7,
        response_format = {"type": "json_object"}
    )

    text = response.choices[0].message.content
    return json.loads(text)

def main():
    for i in range(10):
        try:
            level = generate_level()

            if validate(level):
                print("✅ 合法关卡：")
                print(level)
                break
            else:
                print("❌ 不合法，重试")

        except Exception as e:
            print("解析失败，重试", e)


if __name__ == "__main__":
    main()
