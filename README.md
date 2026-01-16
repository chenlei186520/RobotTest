# 机器人静态测试系统

基于Flask的机器人静态测试系统Web应用，按照指定样式设计。

## 功能特点

- 左侧导航栏：包含9个测试类别
- 右侧内容区：显示选中测试的详细信息
- 测试项目：每个项目都有"正常"和"异常"两个选项（互斥）
- 开始测试按钮：提交测试结果

## 安装和运行

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 运行应用：
```bash
python app.py
```

3. 在浏览器中访问：
```
http://localhost:5000
```

## 项目结构

```
RebotTest/
├── app.py                 # Flask主应用
├── config.py              # 配置文件（超时时间、IO映射、指令等）
├── requirements.txt       # Python依赖
├── test_data/             # 测试数据目录（每个TAB独立文件）
│   ├── __init__.py       # 模块初始化
│   ├── light_test.py     # 灯光测试数据
│   ├── voice_test.py     # 语音测试数据
│   ├── button_test.py    # 按键测试数据
│   ├── touch_test.py     # 触边测试数据
│   ├── display_test.py   # 显示屏测试数据
│   ├── camera_test.py    # 相机/激光/TOF测试数据
│   ├── lift_motor_test.py    # 举升电机测试数据
│   ├── rotation_motor_test.py # 旋转电机测试数据
│   ├── walking_motor_test.py # 行走电机测试数据
│   └── README.md         # 测试数据说明
├── templates/
│   └── index.html        # HTML模板
└── static/
    ├── style.css         # CSS样式
    └── script.js         # JavaScript逻辑
```

## 配置说明

### config.py
包含所有可配置项：
- `IO_CHECK_TIMEOUT`: IO检查超时时间（秒），默认30秒
- `IO_CHECK_INTERVAL`: IO检查轮询间隔（毫秒），默认500ms
- `COMMAND_WAIT_TIME`: 指令发送后等待时间（毫秒），默认1000ms
- `IO_INDEX_MAP`: IO信号索引映射（需要根据实际情况修改）
- `COMMAND_MAP`: 指令映射
- `ROS_TOPIC`: ROS话题名称

### test_data/
每个测试TAB的数据都独立管理，方便后期修改和维护。

## 测试类别

1. 灯光测试
2. 语音测试
3. 按键测试
4. 触边测试
5. 显示屏测试
6. 相机/激光/TOF测试
7. 举升电机测试
8. 旋转电机测试
9. 行走电机测试
