# API模块说明

本目录包含各个测试类别的API处理逻辑，每个测试类别都有独立的API处理器，便于根据不同车型进行定制和优化。

## 文件结构

- `__init__.py` - 模块初始化文件，统一导出所有API处理器
- `base_api.py` - 基础API处理器，提供默认实现
- `light_api.py` - 灯光测试API处理器

## 如何添加新的测试类别API

1. 创建新的API文件，例如 `voice_api.py`
2. 继承 `BaseAPI` 类或实现自定义逻辑
3. 在 `__init__.py` 中注册新的API处理器

示例：

```python
# apis/voice_api.py
from .base_api import BaseAPI

class VoiceAPI(BaseAPI):
    """语音测试专用的API处理器"""
    
    @staticmethod
    def send_command(item_id):
        # 自定义语音测试的指令发送逻辑
        pass
    
    @staticmethod
    def check_io(item_id):
        # 自定义语音测试的IO检查逻辑
        pass
```

然后在 `apis/__init__.py` 中添加：

```python
from .voice_api import VoiceAPI

API_HANDLERS = {
    "light": LightAPI,
    "voice": VoiceAPI,  # 添加新的处理器
    # ...
}
```

## 优势

1. **模块化设计**：每个测试类别独立管理，互不干扰
2. **易于扩展**：新增测试类别只需添加新文件
3. **便于定制**：可以根据不同车型实现不同的API逻辑
4. **代码清晰**：每个API处理器的职责明确
