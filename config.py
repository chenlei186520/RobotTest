# 测试系统配置文件
import re

# IO检查超时时间（秒）
IO_CHECK_TIMEOUT = 30

# TOF订阅超时时间（秒）
TOF_SUBSCRIBE_TIMEOUT = 30

# IO检查轮询间隔（毫秒）
IO_CHECK_INTERVAL = 500

# 指令发送后等待时间（毫秒），再开始检查IO
COMMAND_WAIT_TIME = 1000

# IO信号索引映射（需要根据实际情况调整）
# 请根据实际的int_data数组索引对应关系修改以下映射
# 例如：如果红灯对应int_data[5]，则改为 "red_light": 5
IO_INDEX_MAP = {
    "red_light": 0,      # 红灯对应的IO索引（请根据实际情况修改）
    "yellow_light": 1,   # 黄灯对应的IO索引（请根据实际情况修改）
    "blue_light": 2,     # 蓝灯对应的IO索引（请根据实际情况修改）
    "green_light": 3,    # 绿灯对应的IO索引（请根据实际情况修改）
    "clearance_light": 4 # 示廓灯对应的IO索引（请根据实际情况修改）
}

# 按键测试IO信号索引映射（按车型配置）
# 格式：车型 -> {按钮ID: IO索引}
# 注意：此配置由parse_vehicle_mapping.py自动生成
BUTTON_IO_INDEX_MAP_BY_VEHICLE = {
    "X060": {
        "front_right_confirm": 4,      # 右前确认按钮对应的IO索引
        "back_right_confirm": 11,      # 右后确认按钮对应的IO索引
        "front_right_maintenance": 2,      # 右前维修按钮对应的IO索引
        "back_right_maintenance": 9,      # 右后维修按钮对应的IO索引
        "back_right_emergency": 10,      # 右后急停按钮对应的IO索引
        "front_left_emergency": 3,      # 左前急停按钮对应的IO索引
    },
    "X080": {
        "front_right_confirm": 4,      # 右前确认按钮对应的IO索引
        "back_right_confirm": 11,      # 右后确认按钮对应的IO索引
        "front_right_maintenance": 2,      # 右前维修按钮对应的IO索引
        "back_right_maintenance": 9,      # 右后维修按钮对应的IO索引
        "back_right_emergency": 10,      # 右后急停按钮对应的IO索引
        "front_left_emergency": 3,      # 左前急停按钮对应的IO索引
    },
    "X100": {
        "front_right_confirm": 3,      # 右前确认按钮对应的IO索引
        "back_right_confirm": 9,      # 右后确认按钮对应的IO索引
        "front_right_maintenance": 1,      # 右前维修按钮对应的IO索引
        "back_right_maintenance": 11,      # 右后维修按钮对应的IO索引
        "front_right_emergency": 7,      # 右前急停按钮对应的IO索引
        "back_right_emergency": 7,      # 右后急停按钮对应的IO索引
        "back_left_emergency": 7,      # 左后急停按钮对应的IO索引
        "front_left_emergency": 7,      # 左前急停按钮对应的IO索引
    },
    "X150": {
        "front_right_confirm": 3,      # 右前确认按钮对应的IO索引
        "back_right_confirm": 9,      # 右后确认按钮对应的IO索引
        "front_right_maintenance": 1,      # 右前维修按钮对应的IO索引
        "back_right_maintenance": 11,      # 右后维修按钮对应的IO索引
        "front_right_emergency": 7,      # 右前急停按钮对应的IO索引
        "back_right_emergency": 7,      # 右后急停按钮对应的IO索引
        "back_left_emergency": 7,      # 左后急停按钮对应的IO索引
        "front_left_emergency": 7,      # 左前急停按钮对应的IO索引
    },
    # 可以在这里添加更多车型配置
}

# 触边测试IO信号索引映射（按车型配置）
# 格式：车型 -> {触边ID: IO索引}
TOUCH_IO_INDEX_MAP_BY_VEHICLE = {
    "X060": {
        "front_touch": 1,      # 前触边对应的IO索引
        "back_touch": 8,       # 后触边对应的IO索引
    },
    "X080": {
        "front_touch": 1,      # 前触边对应的IO索引
        "back_touch": 8,       # 后触边对应的IO索引
    },
    "X100": {
        "front_touch": 5,      # 前触边对应的IO索引
        "back_touch": 8,       # 后触边对应的IO索引
    },
    "X150": {
        "front_touch": 5,      # 前触边对应的IO索引
        "back_touch": 8,       # 后触边对应的IO索引
    },
}

# 显示屏测试IO信号索引映射（按车型配置）
# 格式：车型 -> {显示屏测试ID: IO索引}
# 注意：显示屏测试的IO映射需要根据实际情况配置
DISPLAY_IO_INDEX_MAP_BY_VEHICLE = {
    "X060": {
        # 显示屏测试的IO映射（需要根据实际情况填写）
    },
    "X080": {
        # 显示屏测试的IO映射（需要根据实际情况填写）
    },
    "X100": {
        # 显示屏测试的IO映射（需要根据实际情况填写）
    },
    "X150": {
        # 显示屏测试的IO映射（需要根据实际情况填写）
    },
}

# 获取指定车型的按键IO索引映射
def get_button_io_map(vehicle_model):
    """根据车型获取对应的按键IO索引映射"""
    return BUTTON_IO_INDEX_MAP_BY_VEHICLE.get(vehicle_model, BUTTON_IO_INDEX_MAP_BY_VEHICLE.get("X100", {}))

# 获取指定车型的触边IO索引映射
def get_touch_io_map(vehicle_model):
    """根据车型获取对应的触边IO索引映射"""
    return TOUCH_IO_INDEX_MAP_BY_VEHICLE.get(vehicle_model, TOUCH_IO_INDEX_MAP_BY_VEHICLE.get("X100", {}))

# 获取指定车型的显示屏IO索引映射
def get_display_io_map(vehicle_model):
    """根据车型获取对应的显示屏IO索引映射"""
    return DISPLAY_IO_INDEX_MAP_BY_VEHICLE.get(vehicle_model, DISPLAY_IO_INDEX_MAP_BY_VEHICLE.get("X100", {}))

# 按键测试项配置（按车型配置）
# 定义每个车型显示哪些按键测试项
BUTTON_TEST_ITEMS_BY_VEHICLE = {
    "X060": [
        "front_right_maintenance",  # 右前维护按钮
        "front_left_emergency",     # 左前急停按钮
        "front_right_confirm",      # 右前确认按钮
        "back_right_maintenance",   # 右后维护按钮
        "back_right_emergency",     # 右后急停按钮
        "back_right_confirm"        # 右后确认按钮
    ],
    "X080": [
        "front_right_maintenance",  # 右前维护按钮
        "front_left_emergency",     # 左前急停按钮
        "front_right_confirm",      # 右前确认按钮
        "back_right_maintenance",   # 右后维护按钮
        "back_right_emergency",     # 右后急停按钮
        "back_right_confirm"        # 右后确认按钮
    ],
    "X100": [
        "front_right_maintenance",  # 右前维护按钮
        "front_right_confirm",      # 右前确认按钮
        "back_right_emergency",     # 右后急停按钮（与左后急停、右前急停、左前急停共用IO索引7）
        "back_left_emergency",      # 左后急停按钮（与右后急停、右前急停、左前急停共用IO索引7）
        "front_right_emergency",    # 右前急停按钮（与右后急停、左后急停、左前急停共用IO索引7）
        "front_left_emergency",     # 左前急停按钮（与右后急停、左后急停、右前急停共用IO索引7）
        "back_right_confirm",       # 右后确认按钮
        "back_right_maintenance"    # 右后维护按钮
    ],
    "X150": [
        "front_right_maintenance",  # 右前维护按钮
        "front_right_confirm",      # 右前确认按钮
        "back_right_emergency",     # 右后急停按钮（与左后急停、右前急停、左前急停共用IO索引7）
        "back_left_emergency",      # 左后急停按钮（与右后急停、右前急停、左前急停共用IO索引7）
        "front_right_emergency",    # 右前急停按钮（与右后急停、左后急停、左前急停共用IO索引7）
        "front_left_emergency",     # 左前急停按钮（与右后急停、左后急停、右前急停共用IO索引7）
        "back_right_confirm",       # 右后确认按钮
        "back_right_maintenance"    # 右后维护按钮
    ]
}

# 获取指定车型的按键测试项列表
def get_button_test_items(vehicle_model):
    """
    根据车型获取对应的按键测试项ID列表
    支持完整设备型号（如 X-060-V1-LV-2L2T-C-1A-DHF）或简单车型（如 X060）
    """
    import re
    
    # 从完整设备型号中提取车型代码（如从 'X-060-V1-LV-2L2T-C-1A-DHF' 提取 'X060'）
    extracted_vehicle = vehicle_model
    vehicle_match = re.search(r'X[_-]?(\d{3})', vehicle_model)
    if vehicle_match:
        extracted_vehicle = 'X' + vehicle_match.group(1)
        print(f"[按键测试配置] 从设备型号 '{vehicle_model}' 提取车型: '{extracted_vehicle}'")
    else:
        # 如果正则匹配失败，检查是否已经是车型格式（如 X060, X080, X100, X150）
        if re.match(r'^X\d{3}$', vehicle_model):
            extracted_vehicle = vehicle_model
            print(f"[按键测试配置] '{vehicle_model}' 已经是车型格式，直接使用")
    
    # 根据提取的车型获取对应的按键测试项
    return BUTTON_TEST_ITEMS_BY_VEHICLE.get(extracted_vehicle, BUTTON_TEST_ITEMS_BY_VEHICLE.get("X100", []))

# 灯光测试指令映射
COMMAND_MAP = {
    "red_light": "echo -e -n '\\x5A\\x4E\\x00\\x05\\x04\\x02\\x32\\x01\\x00\\x5D' > /dev/ttyACM0",
    "yellow_light": "echo -e -n '\\x5A\\x4E\\x00\\x05\\x04\\x02\\x32\\x01\\x03\\x1D' > /dev/ttyACM0",
    "blue_light": "echo -e -n '\\x5A\\x4E\\x00\\x05\\x04\\x02\\x32\\x01\\x02\\xDC' > /dev/ttyACM0",
    "white_light_blink": "echo -e -n '\\x5A\\x4E\\x00\\x05\\x04\\x02\\x32\\x01\\x04\\x5C' > /dev/ttyACM0",
    "green_light": "echo -e -n '\\x5A\\x4E\\x00\\x05\\x04\\x02\\x32\\x01\\x01\\x9C' > /dev/ttyACM0",
    "clearance_light": "echo -e -n '\\x5A\\x4A\\x00\\x09\\x1F\\x00\\x00\\x00\\x20\\x00\\x00\\x00\\x20\\x1E' > /dev/ttyACM0",  # 示廓灯开
    "clearance_light_off": "echo -e -n '\\x5A\\x4A\\x00\\x09\\x1F\\x00\\x00\\x00\\x20\\x00\\x00\\x00\\x00\\x1F' > /dev/ttyACM0"  # 示廓灯关
}

# 关闭所有灯指令（灯光测试选择结果后自动执行）
TURN_OFF_ALL_LIGHTS_COMMAND = "echo -e -n '\\x5A\\x4E\\x00\\x05\\x04\\x00\\x00\\x00\\x00\\xFC' > /dev/ttyACM0"

# 语音测试指令映射
VOICE_COMMAND_MAP = {
    "voice_broadcast": "echo -e -n '\\x5A\\x4E\\x00\\x05\\x04\\x02\\x32\\x01\\x00\\x5D' > /dev/ttyACM0"
}

# 举升电机测试指令映射
# 格式：高度(mm) -> {动作: SSH指令}
# 动作：'lift_up' (举升) 或 'lift_down' (放下)
LIFT_MOTOR_COMMAND_MAP = {
    50: {
        "lift_up": "echo -e -n '\\x5A\\x4E\\x00\\x05\\x04\\x02\\x32\\x01\\x00\\x5D' > /dev/ttyACM0",
        "lift_down": "echo -e -n '\\x5A\\x4E\\x00\\x05\\x04\\x02\\x32\\x01\\x00\\x5D' > /dev/ttyACM0"
    },
    60: {
        "lift_up": "echo -e -n '\\x5A\\x4E\\x00\\x05\\x04\\x02\\x32\\x01\\x00\\x5D' > /dev/ttyACM0",
        "lift_down": "echo -e -n '\\x5A\\x4E\\x00\\x05\\x04\\x02\\x32\\x01\\x00\\x5D' > /dev/ttyACM0"
    }
}

# 举升电机测试默认高度（毫米）
LIFT_MOTOR_DEFAULT_HEIGHT = 60

# 旋转电机测试指令映射
# 格式：角度(度) -> {动作: SSH指令}
# 动作：'rotate' (旋转) 或 'reset' (归零)
# 注意：归零指令不依赖角度，统一使用RESET_COMMAND
ROTATION_MOTOR_COMMAND_MAP = {
    90: {
        "rotate": "echo -e -n '\\x5A\\x4E\\x00\\x05\\x04\\x02\\x32\\x01\\x00\\x5D' > /dev/ttyACM0"
    },
    70: {
        "rotate": "echo -e -n '\\x5A\\x4E\\x00\\x05\\x04\\x02\\x32\\x01\\x00\\x5D' > /dev/ttyACM0"
    }
}

# 旋转电机归零指令（不依赖角度，统一指令）
ROTATION_MOTOR_RESET_COMMAND = "echo -e -n '\\x5A\\x4E\\x00\\x05\\x04\\x02\\x32\\x01\\x00\\x5D' > /dev/ttyACM0"

# 旋转电机测试默认角度（度）
ROTATION_MOTOR_DEFAULT_ANGLE = 90

# 行走电机测试指令映射
# 格式：时间(秒) -> {动作: SSH指令}
# 动作：'forward' (前进) 或 'backward' (后退)
WALKING_MOTOR_COMMAND_MAP = {
    10: {
        "forward": "echo -e -n '\\x5A\\x4E\\x00\\x05\\x04\\x02\\x32\\x01\\x00\\x5D' > /dev/ttyACM0",
        "backward": "echo -e -n '\\x5A\\x4E\\x00\\x05\\x04\\x02\\x32\\x01\\x00\\x5D' > /dev/ttyACM0"
    },
    20: {
        "forward": "echo -e -n '\\x5A\\x4E\\x00\\x05\\x04\\x02\\x32\\x01\\x00\\x5D' > /dev/ttyACM0",
        "backward": "echo -e -n '\\x5A\\x4E\\x00\\x05\\x04\\x02\\x32\\x01\\x00\\x5D' > /dev/ttyACM0"
    }
}

# 行走电机测试默认时间（秒）
WALKING_MOTOR_DEFAULT_TIME = 10

# ROS话题配置
ROS_TOPIC = "/Dev_input_output"
ROS_COMMAND_TIMEOUT = 35  # rostopic命令超时时间（秒），应大于IO_CHECK_TIMEOUT

# TOF订阅话题配置
TOF_FRONT_TOPIC = "/berxel_camera1/tof_cloudpoint"  # 前TOF订阅话题
TOF_REAR_TOPIC = "/berxel_camera2/tof_cloudpoint"   # 后TOF订阅话题

# SSH配置
SSH_USER = "robot"  # SSH用户名（可根据实际情况修改）
SSH_PASSWORD = "robot"  # SSH密码（可根据实际情况修改）
SSH_TIMEOUT = 10   # SSH连接超时时间（秒）
SSH_KEY_PATH = None  # SSH密钥路径（如果使用密钥认证，设置此路径；如果为None，使用密码认证）
SSH_CONNECTION_HOLD_TIME = 30  # SSH连接保持时间（秒），按钮点击后保持连接的时间
# 注意：使用SSH密码认证需要安装paramiko库：pip install paramiko

# 车型TAB显示配置
# 定义每个车型显示哪些测试TAB
# 格式：车型名称 -> TAB ID列表（按顺序）
VEHICLE_TAB_CONFIG = {
    "X100": [
        "light",          # 灯光测试
        "voice",          # 语音测试
        "button",         # 按键测试
        "touch",          # 触边测试
        "display",        # 显示屏测试
        "camera",         # 相机/激光/TOF测试
        "lift_motor",     # 举升电机测试
        "rotation_motor", # 旋转电机测试
        "walking_motor"   # 行走电机测试
    ],
    "X200": [
        "light",          # 灯光测试
        "voice",          # 语音测试
        "button"          # 按键测试
    ],
    "X300": [
        "light",          # 灯光测试
        "voice",          # 语音测试
        "button",         # 按键测试
        "touch",          # 触边测试
        "display",        # 显示屏测试
        "camera"          # 相机/激光/TOF测试
    ]
    # 可以在这里添加更多车型配置
}

# 相机/激光/TOF测试设备显示配置
# 定义每个车型显示哪些设备
# 格式：车型名称 -> 设备ID列表（按顺序）
CAMERA_DEVICE_CONFIG = {
    "X100": [
        "upper_camera",   # 上相机
        "lower_camera",   # 下相机
        "front_laser",    # 前激光
        "rear_laser",     # 后激光
        "front_tof",      # 前TOF
        "rear_tof"        # 后TOF
    ],
    "X300": [
        "upper_camera",   # 上相机
        "lower_camera",   # 下相机
        "front_laser"     # 前激光
    ]
    # 可以在这里添加更多车型配置
    # "X400": ["upper_camera", "lower_camera", ...],
}

# 相机/激光/TOF设备IP地址映射（按车型配置）
# 格式：车型名称 -> {设备ID: IP地址}
CAMERA_IP_MAP_BY_VEHICLE = {
    "X100": {
        "upper_camera": "192.168.1.60",   # 上相机IP地址
        "lower_camera": "192.168.1.61",   # 下相机IP地址
        "front_laser": "192.168.1.100",    # 前激光IP地址
        "rear_laser": "192.168.1.88",     # 后激光IP地址
        "front_tof": "10.2.129.234",      # 前TOF IP地址
        "rear_tof": "10.2.129.239"        # 后TOF IP地址
    },
    "X300": {
        "upper_camera": "10.2.129.230",   # 上相机IP地址
        "lower_camera": "10.2.129.231",   # 下相机IP地址
        "front_laser": "10.2.129.232"     # 前激光IP地址
    }
    # 可以在这里添加更多车型配置
    # "X400": {
    #     "upper_camera": "10.2.129.230",
    #     ...
    # },
}

# 获取指定车型的设备IP地址映射
def get_camera_ip_map(vehicle_model):
    """根据车型获取对应的设备IP地址映射"""
    return CAMERA_IP_MAP_BY_VEHICLE.get(vehicle_model, CAMERA_IP_MAP_BY_VEHICLE.get("X100", {}))

# 获取指定车型的相机测试设备列表
def get_camera_devices(vehicle_model):
    """根据车型获取对应的相机测试设备列表"""
    return CAMERA_DEVICE_CONFIG.get(vehicle_model, CAMERA_DEVICE_CONFIG.get("X100", []))

# Ping测试超时时间（秒）
PING_TEST_TIMEOUT = 10

# 解析devices_data.csv文件，根据车型和按钮名称匹配int_data下标和值的含义
def parse_button_mapping_from_csv(vehicle_model, button_name):
    """
    根据车型和按钮名称，从CSV文件中查找对应的int_data下标和值的含义
    
    参数:
        vehicle_model: 车型（可能是完整设备型号如 'X-060-V1-LV-2L2T-C-1A-DHF'，或简单车型如 'X060'）
        button_name: 按钮名称（如 '右前维护按钮', '左前急停按钮'）
    
    返回:
        dict: {
            'io_index': int,  # int_data下标
            'value_meaning': str,  # 值的含义（如 '0表示按下 1表示弹起'）
            'button_name': str  # 匹配到的按钮名称
        } 或 None（如果未找到）
    """
    import csv
    import os
    import re
    
    csv_path = os.path.join(os.path.dirname(__file__), 'test_data', 'devices_data.csv')
    
    # 从完整设备型号中提取车型代码（如从 'X-060-V1-LV-2L2T-C-1A-DHF' 提取 'X060'）
    # 支持格式：X-060-... 或 X060-... 或 X060
    extracted_vehicle = vehicle_model
    vehicle_match = re.search(r'X[_-]?(\d{3})', vehicle_model)
    if vehicle_match:
        extracted_vehicle = 'X' + vehicle_match.group(1)
        print(f"[CSV解析调试] 从设备型号 '{vehicle_model}' 提取车型: '{extracted_vehicle}'")
    else:
        # 如果正则匹配失败，检查是否已经是车型格式（如 X060, X080, X100, X150）
        # 如果已经是车型格式，直接使用
        if re.match(r'^X\d{3}$', vehicle_model):
            extracted_vehicle = vehicle_model
            print(f"[CSV解析调试] '{vehicle_model}' 已经是车型格式，直接使用")
        else:
            print(f"[CSV解析调试] 无法从 '{vehicle_model}' 提取车型，使用原始值")
    
    # 尝试不同的编码
    encodings = ['utf-8', 'gbk', 'gb2312', 'utf-8-sig']
    
    for encoding in encodings:
        try:
            with open(csv_path, 'r', encoding=encoding) as f:
                reader = csv.reader(f)
                rows = list(reader)
                
                if len(rows) < 1:
                    continue
                
                # 读取表头，自动匹配车型对应的列
                header = rows[0]
                name_col = None
                desc_col = None
                
                # 在表头中查找包含当前车型的列（包含关系匹配）
                # 使用提取出的车型代码进行匹配
                for col_idx, col_name in enumerate(header):
                    col_name_str = str(col_name).strip()
                    # 检查列名是否包含提取出的车型（包含关系：只要车型字符串在列名中即匹配）
                    # 例如：X060 在 "X150/X100/X060" 中 → 匹配成功
                    #       X080 在 "X061/X080" 中 → 匹配成功
                    if extracted_vehicle in col_name_str:
                        # 找到车型列，确定按钮名称列
                        name_col = col_idx
                        
                        # 查找对应的"值的含义"列
                        # 值的含义列通常在按钮名称列的下一列，且表头包含"值的含义"
                        # 遍历后续列，查找"值的含义"列
                        for next_col_idx in range(col_idx + 1, len(header)):
                            next_col_name = str(header[next_col_idx]).strip()
                            if '值的含义' in next_col_name or '含义' in next_col_name:
                                desc_col = next_col_idx
                                break
                        
                        # 如果没找到明确的"值的含义"列，使用下一列作为默认
                        if desc_col is None and col_idx + 1 < len(header):
                            desc_col = col_idx + 1
                        
                        print(f"[CSV解析调试] 车型 '{extracted_vehicle}' (从 '{vehicle_model}' 提取) 自动匹配到列: '{col_name_str}' (按钮名称列索引: {name_col}, 值的含义列索引: {desc_col})")
                        break
                
                # 如果没找到匹配的列，返回None
                if name_col is None or desc_col is None:
                    print(f"[CSV解析调试] 警告: 未找到车型 '{extracted_vehicle}' (从 '{vehicle_model}' 提取) 对应的列，表头: {header}")
                    continue
                
                # 跳过表头，从第二行开始
                for row in rows[1:]:
                    if len(row) < max(name_col, desc_col) + 1:
                        continue
                    
                    # 第一列是int_data下标
                    index_str = str(row[0]).strip()
                    if not index_str or not index_str.isdigit():
                        continue
                    
                    io_index = int(index_str)
                    
                    # 获取按钮名称列
                    button_name_in_csv = str(row[name_col]).strip() if len(row) > name_col else ""
                    # 获取值的含义列
                    value_meaning = str(row[desc_col]).strip() if len(row) > desc_col else ""
                    
                    if not button_name_in_csv:
                        continue
                    
                    # 调试：打印正在检查的行
                    print(f"[CSV解析调试] 检查行 {io_index}: CSV按钮名称='{button_name_in_csv}', 查找按钮='{button_name}'")
                    
                    # 处理多个按钮的情况（用空格分隔）
                    button_names = [name.strip() for name in button_name_in_csv.split() if name.strip()]
                    
                    # 匹配按钮名称（支持部分匹配，如"右前维护按钮"匹配"右前维护键"）
                    # 同时支持"维修"和"维护"、"键"和"按钮"的匹配
                    for csv_button_name in button_names:
                        # 移除括号中的内容进行匹配（如"右前维护按钮（需要按一段时间）"匹配"右前维护按钮"）
                        csv_button_name_clean = re.sub(r'[（(].*?[）)]', '', csv_button_name)
                        button_name_clean = re.sub(r'[（(].*?[）)]', '', button_name)
                        
                        # 统一"维修"和"维护"为"维护"进行匹配
                        # 统一"键"和"按钮"为"键"进行匹配
                        csv_button_name_normalized = csv_button_name_clean.replace('维修', '维护').replace('按钮', '键')
                        button_name_normalized = button_name_clean.replace('维修', '维护').replace('按钮', '键')
                        
                        # 检查是否匹配（支持部分匹配）
                        # 使用完全匹配或包含匹配
                        # 先检查原始名称是否完全匹配（最优先）
                        if button_name_clean == csv_button_name_clean:
                            print(f"[CSV解析调试] 匹配成功: '{button_name}' -> '{csv_button_name}' (IO索引: {io_index})")
                            return {
                                'io_index': io_index,
                                'value_meaning': value_meaning,
                                'button_name': csv_button_name
                            }
                        
                        # 再检查标准化后的名称是否匹配
                        if (button_name_normalized == csv_button_name_normalized or
                            button_name_normalized in csv_button_name_normalized or 
                            csv_button_name_normalized in button_name_normalized):
                            print(f"[CSV解析调试] 匹配成功: '{button_name}' -> '{csv_button_name}' (IO索引: {io_index})")
                            return {
                                'io_index': io_index,
                                'value_meaning': value_meaning,
                                'button_name': csv_button_name
                            }
                        
                        # 最后检查原始名称的包含关系
                        if (button_name_clean in csv_button_name_clean or 
                            csv_button_name_clean in button_name_clean):
                            print(f"[CSV解析调试] 匹配成功: '{button_name}' -> '{csv_button_name}' (IO索引: {io_index})")
                            return {
                                'io_index': io_index,
                                'value_meaning': value_meaning,
                                'button_name': csv_button_name
                            }
                
                # 如果所有编码都失败，返回None
                break
        except Exception as e:
            print(f"[CSV解析] 使用 {encoding} 编码失败: {e}")
            continue
    
    return None
