import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from search import AISearchEngine

print("开始测试get_supported_categories方法...")

# 创建搜索引擎实例
sengine = AISearchEngine()
print("已创建AISearchEngine实例")

# 尝试获取支持的类别
try:
    print("调用get_supported_categories()...")
    categories = sengine.get_supported_categories()
    print("成功获取支持的类别：")
    print(categories)
    print(f"类别总数：{len(categories)}")
except Exception as e:
    print(f"获取类别时出错：{type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
finally:
    print("测试完成")