import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 打印环境变量
print("AIHUBMIX_API_KEY:", os.getenv("AIHUBMIX_API_KEY"))
print("API key length:", len(os.getenv("AIHUBMIX_API_KEY")) if os.getenv("AIHUBMIX_API_KEY") else 0)
