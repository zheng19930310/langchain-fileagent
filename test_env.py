"""
测试环境变量加载
"""
import os
from dotenv import load_dotenv

print("=" * 60)
print("测试环境变量加载")
print("=" * 60)

# 测试1：加载 .env 文件
print("\n[测试1] 加载 .env 文件...")
env_path = os.path.join(os.path.dirname(__file__), '.env')
print(f"  .env 文件路径: {env_path}")
print(f"  .env 文件存在: {os.path.exists(env_path)}")

if os.path.exists(env_path):
    with open(env_path, 'r', encoding='utf-8') as f:
        print(f"  .env 文件内容:")
        for line in f.readlines():
            line = line.strip()
            if line and not line.startswith('#'):
                # 隐藏 API Key 的敏感部分
                if 'KEY' in line:
                    key_name, key_value = line.split('=', 1)
                    print(f"    {key_name}={key_value[:10]}*** (已隐藏)")
                else:
                    print(f"    {line}")

# 测试2：加载前检查环境变量
print("\n[测试2] 加载前的环境变量...")
print(f"  OPENAI_API_KEY: {os.getenv('OPENAI_API_KEY', '未设置')}")
print(f"  OPENAI_MODEL: {os.getenv('OPENAI_MODEL', '未设置')}")
print(f"  OPENAI_BASE_URL: {os.getenv('OPENAI_BASE_URL', '未设置')}")

# 测试3：加载 .env 文件
print("\n[测试3] 执行 load_dotenv()...")
result = load_dotenv()
print(f"  加载结果: {result}")

# 测试4：加载后检查环境变量
print("\n[测试4] 加载后的环境变量...")
api_key = os.getenv('OPENAI_API_KEY')
model = os.getenv('OPENAI_MODEL')
base_url = os.getenv('OPENAI_BASE_URL')

print(f"  OPENAI_API_KEY: {api_key[:15]}*** (已隐藏)" if api_key else "  OPENAI_API_KEY: 未设置")
print(f"  OPENAI_MODEL: {model}")
print(f"  OPENAI_BASE_URL: {base_url}")

# 测试5：验证配置
print("\n[测试5] 配置验证...")
if not api_key or api_key == '':
    print("  ❌ 错误: OPENAI_API_KEY 为空")
elif api_key == 'sk-your-openai-api-key-here':
    print("  ❌ 错误: OPENAI_API_KEY 仍然是示例值")
else:
    print("  ✅ OPENAI_API_KEY 已正确配置")

if model:
    print(f"  ✅ OPENAI_MODEL: {model}")
else:
    print("  ️  OPENAI_MODEL 未设置，将使用默认值")

if base_url:
    print(f"  ✅ OPENAI_BASE_URL: {base_url}")
else:
    print("  ️  OPENAI_BASE_URL 未设置，将使用默认值")

print("\n" + "=" * 60)
