# 测试数据目录说明

本目录包含各个测试TAB页面的数据配置，每个测试类别都有独立的文件，方便后期维护和修改。

## 文件结构

- `__init__.py` - 模块初始化文件，统一导出所有测试数据
- `light_test.py` - 灯光测试数据
- `voice_test.py` - 语音测试数据
- `button_test.py` - 按键测试数据
- `touch_test.py` - 触边测试数据
- `display_test.py` - 显示屏测试数据
- `camera_test.py` - 相机/激光/TOF测试数据
- `lift_motor_test.py` - 举升电机测试数据
- `rotation_motor_test.py` - 旋转电机测试数据
- `walking_motor_test.py` - 行走电机测试数据

## 如何修改测试数据

1. 找到对应的测试数据文件（如 `light_test.py`）
2. 修改其中的数据结构
3. 保存文件，Flask应用会自动重新加载（debug模式）

## 数据结构格式

每个测试数据文件包含一个字典，格式如下：

```python
TEST_DATA = {
    "sections": [
        {
            "title": "章节标题",
            "items": [
                {"name": "测试项名称", "id": "测试项ID"},
                ...
            ]
        },
        ...
    ]
}
```
