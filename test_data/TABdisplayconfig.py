# TAB显示配置模块
# 从CSV文件中读取设备型号对应的TAB显示策略

import csv
import os
import re

# CSV文件路径
CSV_FILE_PATH = os.path.join(os.path.dirname(__file__), 'TABdisplay_data.csv')

# TAB名称到ID的映射
TAB_NAME_TO_ID = {
    "灯光测试": "light",
    "语音测试": "voice",
    "按键测试": "button",
    "触边测试": "touch",
    "显示屏测试": "display",
    "相机/激光/TOF测试": "camera",
    "举升电机测试": "lift_motor",
    "旋转电机测试": "rotation_motor",
    "行走电机测试": "walking_motor",
}

# 相机设备名称到ID的映射
CAMERA_DEVICE_NAME_TO_ID = {
    "上相机": "upper_camera",
    "下相机": "lower_camera",
    "前激光": "front_laser",
    "后激光": "rear_laser",
    "前TOF": "front_tof",
    "后TOF": "rear_tof",
}

# 缓存解析后的配置（避免重复读取CSV）
_tab_config_cache = None


def load_tab_config_from_csv():
    """
    从CSV文件中加载TAB显示配置
    
    返回:
        dict: {设备型号: {'tabs': [tab_id列表], 'camera_devices': [设备ID列表]}}
    """
    global _tab_config_cache
    
    # 如果已经缓存，直接返回
    if _tab_config_cache is not None:
        return _tab_config_cache
    
    config = {}
    
    # 尝试不同的编码
    encodings = ['utf-8', 'gbk', 'gb2312', 'utf-8-sig']
    
    for encoding in encodings:
        try:
            with open(CSV_FILE_PATH, 'r', encoding=encoding) as f:
                reader = csv.reader(f)
                rows = list(reader)
                
                if len(rows) < 2:
                    print(f"[TAB配置] 警告: CSV文件行数不足（至少需要表头+1行数据）")
                    break
                
                # 跳过表头
                for row in rows[1:]:
                    if len(row) < 2:
                        continue
                    
                    device_model = row[0].strip()
                    tab_strategy = row[1].strip()
                    
                    if not device_model or not tab_strategy:
                        continue
                    
                    # 解析TAB策略（多行字符串，用换行符分隔）
                    tab_lines = [line.strip() for line in tab_strategy.split('\n') if line.strip()]
                    
                    tab_ids = []
                    camera_devices = []
                    
                    for tab_line in tab_lines:
                        # 处理相机/激光/TOF测试的特殊情况
                        if tab_line.startswith("相机/激光/TOF测试"):
                            tab_ids.append("camera")
                            
                            # 解析设备描述（格式：相机/激光/TOF测试--上下相机/前后激光）
                            # 提取"--"后面的部分
                            if "--" in tab_line:
                                device_desc = tab_line.split("--", 1)[1].strip()
                                # 解析设备列表（用"/"分隔）
                                device_names = [name.strip() for name in device_desc.split("/") if name.strip()]
                                
                                # 将设备名称映射到ID（支持组合名称，如"上下相机"拆分为"上相机"和"下相机"）
                                for device_name in device_names:
                                    # 处理组合名称
                                    if "上下" in device_name and "相机" in device_name:
                                        # "上下相机" -> "上相机" + "下相机"
                                        for single_name in ["上相机", "下相机"]:
                                            if single_name in CAMERA_DEVICE_NAME_TO_ID:
                                                device_id = CAMERA_DEVICE_NAME_TO_ID[single_name]
                                                if device_id not in camera_devices:
                                                    camera_devices.append(device_id)
                                    elif "前后" in device_name and "激光" in device_name:
                                        # "前后激光" -> "前激光" + "后激光"
                                        for single_name in ["前激光", "后激光"]:
                                            if single_name in CAMERA_DEVICE_NAME_TO_ID:
                                                device_id = CAMERA_DEVICE_NAME_TO_ID[single_name]
                                                if device_id not in camera_devices:
                                                    camera_devices.append(device_id)
                                    elif "前后" in device_name and "TOF" in device_name:
                                        # "前后TOF" -> "前TOF" + "后TOF"
                                        for single_name in ["前TOF", "后TOF"]:
                                            if single_name in CAMERA_DEVICE_NAME_TO_ID:
                                                device_id = CAMERA_DEVICE_NAME_TO_ID[single_name]
                                                if device_id not in camera_devices:
                                                    camera_devices.append(device_id)
                                    elif device_name in CAMERA_DEVICE_NAME_TO_ID:
                                        # 单个设备名称，直接映射
                                        device_id = CAMERA_DEVICE_NAME_TO_ID[device_name]
                                        if device_id not in camera_devices:
                                            camera_devices.append(device_id)
                            else:
                                # 如果没有设备描述，使用默认设备（上相机、下相机、前激光、后激光）
                                default_devices = ["upper_camera", "lower_camera", "front_laser", "rear_laser"]
                                camera_devices = default_devices
                        else:
                            # 普通TAB，直接映射
                            if tab_line in TAB_NAME_TO_ID:
                                tab_id = TAB_NAME_TO_ID[tab_line]
                                if tab_id not in tab_ids:
                                    tab_ids.append(tab_id)
                    
                    config[device_model] = {
                        'tabs': tab_ids,
                        'camera_devices': camera_devices
                    }
                
                # 成功解析，缓存结果
                _tab_config_cache = config
                print(f"[TAB配置] 成功加载 {len(config)} 个设备型号的TAB配置")
                break
                
        except Exception as e:
            print(f"[TAB配置] 使用 {encoding} 编码读取CSV失败: {e}")
            continue
    
    if not config:
        print(f"[TAB配置] 警告: 未能从CSV文件中加载任何配置")
    
    return config


def get_tabs_by_device_model(device_model):
    """
    根据设备型号获取对应的TAB ID列表
    
    参数:
        device_model: 设备型号（如 "X-060-V1-LV-2L-C-1A"）
    
    返回:
        dict: {
            'tabs': [tab_id列表],
            'camera_devices': [相机设备ID列表]（如果包含camera tab）
        } 或 None（如果未找到）
    """
    config = load_tab_config_from_csv()
    
    if device_model in config:
        return config[device_model]
    
    # 如果精确匹配失败，尝试模糊匹配（支持部分匹配）
    for model, tab_config in config.items():
        if device_model in model or model in device_model:
            print(f"[TAB配置] 使用模糊匹配: {device_model} -> {model}")
            return tab_config
    
    print(f"[TAB配置] 警告: 未找到设备型号 '{device_model}' 的TAB配置")
    return None


def get_camera_devices_by_device_model(device_model):
    """
    根据设备型号获取相机测试需要显示的设备列表
    
    参数:
        device_model: 设备型号
    
    返回:
        list: 设备ID列表，如果未找到或没有相机测试则返回默认列表
    """
    config = get_tabs_by_device_model(device_model)
    
    if config and 'camera_devices' in config and config['camera_devices']:
        return config['camera_devices']
    
    # 默认设备列表
    return ["upper_camera", "lower_camera", "front_laser", "rear_laser"]
