# -*- coding: utf-8 -*-
"""
解析车型订阅匹配数据CSV文件，并更新config.py配置
"""
import csv
import re

def parse_csv_file(file_path):
    """解析CSV文件，提取车型和IO索引映射"""
    mappings = {}
    
    # 尝试不同的编码
    encodings = ['utf-8', 'gbk', 'gb2312', 'utf-8-sig']
    
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                reader = csv.reader(f)
                rows = list(reader)
                
                if len(rows) > 0:
                    print(f"成功使用 {encoding} 编码读取文件")
                    print(f"总行数: {len(rows)}")
                    break
        except Exception as e:
            print(f"使用 {encoding} 编码失败: {e}")
            continue
    else:
        print("所有编码尝试失败")
        return mappings
    
    # 解析数据
    x060_data = {}  # {io_index: button_id}
    x150_data = {}  # {io_index: button_id}
    
    for i, row in enumerate(rows[1:], start=1):  # 跳过表头
        if not row or len(row) < 5:
            continue
        
        # 第一列是int_data索引
        index_str = str(row[0]).strip()
        if not index_str or not index_str.isdigit():
            continue
        
        io_index = int(index_str)
        
        # X060/X080列 (第2列) - 按钮名称
        x060_name = str(row[1]).strip() if len(row) > 1 else ""
        # X150/X100列 (第4列) - 按钮名称
        x150_name = str(row[3]).strip() if len(row) > 3 else ""
        
        # 解析X060/X080的按钮
        if x060_name:
            # 处理多个按钮的情况（如"右后急停键 左后急停键"）
            button_names = []
            if ' ' in x060_name:
                button_names = [name.strip() for name in x060_name.split() if name.strip()]
            else:
                button_names = [x060_name.strip()]
            
            # 使用列表存储同一个IO索引对应的所有按钮
            if io_index not in x060_data:
                x060_data[io_index] = []
            
            for name in button_names:
                button_id = parse_button_name_to_id(name)
                if button_id:
                    # 将按钮ID添加到列表中（去重）
                    if button_id not in x060_data[io_index]:
                        x060_data[io_index].append(button_id)
                        print(f"X060/X080: IO索引{io_index} -> {name} -> {button_id}")
        
        # 解析X150/X100的按钮
        if x150_name:
            # 处理多个按钮的情况（如"右后急停键 左后急停键 右前急停键 左后急停键"）
            # 先尝试按空格分割，如果不行，尝试按常见分隔符分割
            button_names = []
            if ' ' in x150_name:
                button_names = [name.strip() for name in x150_name.split() if name.strip()]
            else:
                # 如果没有空格，可能是单个按钮
                button_names = [x150_name.strip()]
            
            # 使用列表存储同一个IO索引对应的所有按钮
            if io_index not in x150_data:
                x150_data[io_index] = []
            
            for name in button_names:
                button_id = parse_button_name_to_id(name)
                if button_id:
                    # 将按钮ID添加到列表中（去重）
                    if button_id not in x150_data[io_index]:
                        x150_data[io_index].append(button_id)
                        print(f"X150/X100: IO索引{io_index} -> {name} -> {button_id}")
    
    # 构建映射字典 - 注意：需要反转，从button_id到io_index
    # 但需要处理多个按钮共享同一个IO索引的情况
    if x060_data:
        # 反转映射：{button_id: io_index}
        x060_mapping = {}
        # x060_data现在是 {io_index: [button_id1, button_id2, ...]}
        for io_index, button_ids in x060_data.items():
            # 为每个按钮创建映射
            for button_id in button_ids:
                x060_mapping[button_id] = io_index
        
        mappings['X060'] = x060_mapping
        mappings['X080'] = x060_mapping.copy()  # X080和X060使用相同映射
    
    if x150_data:
        # 反转映射：{button_id: io_index}
        x150_mapping = {}
        # x150_data现在是 {io_index: [button_id1, button_id2, ...]}
        for io_index, button_ids in x150_data.items():
            # 为每个按钮创建映射
            for button_id in button_ids:
                x150_mapping[button_id] = io_index
        
        mappings['X100'] = x150_mapping
        mappings['X150'] = x150_mapping.copy()  # X150和X100使用相同映射
    
    return mappings

def parse_button_name_to_id(button_name):
    """将按钮名称转换为ID"""
    # 清理名称，移除括号内容
    name = re.sub(r'（.*?）', '', button_name).strip()
    
    # 映射规则 - 注意顺序，先匹配更具体的
    if '右前确认' in name or '右前确认键' in name:
        return 'front_right_confirm'
    elif '右后确认' in name or '右后确认键' in name:
        return 'back_right_confirm'
    elif '右前维护' in name or '右前维修' in name or '右前维护键' in name:
        return 'front_right_maintenance'
    elif '右后维护' in name or '右后维修' in name or '右后维护键' in name:
        return 'back_right_maintenance'
    elif '右前急停' in name or '右前急停键' in name:
        return 'front_right_emergency'
    elif '右后急停' in name or '右后急停键' in name:
        return 'back_right_emergency'
    elif '左前急停' in name or '左前急停键' in name:
        return 'front_left_emergency'
    elif '左后急停' in name or '左后急停键' in name:
        return 'back_left_emergency'
    
    # 触边不在按键测试中，返回None
    if '触边' in name:
        return None
    
    return None

def update_config_file(mappings):
    """更新config.py文件中的BUTTON_IO_INDEX_MAP_BY_VEHICLE配置"""
    config_file = 'config.py'
    
    # 读取config.py
    with open(config_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 生成新的配置代码
    config_lines = []
    config_lines.append("# 按键测试IO信号索引映射（按车型配置）")
    config_lines.append("# 格式：车型 -> {按钮ID: IO索引}")
    config_lines.append("# 注意：此配置由parse_vehicle_mapping.py自动生成")
    config_lines.append("BUTTON_IO_INDEX_MAP_BY_VEHICLE = {")
    
    # 按车型排序
    vehicle_order = ['X060', 'X080', 'X100', 'X150', 'X200']
    for vehicle in vehicle_order:
        if vehicle in mappings:
            config_lines.append(f'    "{vehicle}": {{')
            # 按按钮ID排序
            button_order = [
                'front_right_confirm', 'back_right_confirm',
                'front_right_maintenance', 'back_right_maintenance',
                'front_right_emergency', 'back_right_emergency',
                'front_left_emergency', 'back_left_emergency'
            ]
            for button_id in button_order:
                if button_id in mappings[vehicle]:
                    io_index = mappings[vehicle][button_id]
                    # 获取按钮中文名称用于注释
                    button_names = {
                        'front_right_confirm': '右前确认按钮',
                        'back_right_confirm': '右后确认按钮',
                        'front_right_maintenance': '右前维修按钮',
                        'back_right_maintenance': '右后维修按钮',
                        'front_right_emergency': '右前急停按钮',
                        'back_right_emergency': '右后急停按钮',
                        'front_left_emergency': '左前急停按钮',
                        'back_left_emergency': '左后急停按钮'
                    }
                    comment = button_names.get(button_id, '')
                    config_lines.append(f'        "{button_id}": {io_index},      # {comment}对应的IO索引')
            config_lines.append('    },')
    
    config_lines.append("    # 可以在这里添加更多车型配置")
    config_lines.append("}")
    
    new_config = '\n'.join(config_lines)
    
    # 替换BUTTON_IO_INDEX_MAP_BY_VEHICLE部分
    pattern = r'# 按键测试IO信号索引映射.*?^}'
    import re
    new_content = re.sub(pattern, new_config, content, flags=re.MULTILINE | re.DOTALL)
    
    # 如果替换失败，手动查找并替换
    if new_content == content:
        # 查找BUTTON_IO_INDEX_MAP_BY_VEHICLE的开始和结束位置
        start_pattern = r'BUTTON_IO_INDEX_MAP_BY_VEHICLE\s*=\s*\{'
        end_pattern = r'^\s*\}\s*$'
        
        lines = content.split('\n')
        start_idx = None
        end_idx = None
        
        for i, line in enumerate(lines):
            if re.search(start_pattern, line):
                start_idx = i
            if start_idx is not None and re.search(end_pattern, line) and i > start_idx:
                # 检查是否是BUTTON_IO_INDEX_MAP_BY_VEHICLE的结束
                # 简单检查：如果下一行是get_button_io_map函数，则这是结束
                if i + 1 < len(lines) and 'get_button_io_map' in lines[i + 1]:
                    end_idx = i
                    break
        
        if start_idx is not None and end_idx is not None:
            # 替换这部分
            new_lines = lines[:start_idx] + new_config.split('\n') + lines[end_idx + 1:]
            new_content = '\n'.join(new_lines)
    
    # 写回文件
    with open(config_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"\n已更新 {config_file} 文件")

if __name__ == '__main__':
    csv_file = 'test_data/devices_data.csv'
    print(f"开始解析 {csv_file}...")
    mappings = parse_csv_file(csv_file)
    
    print("\n解析结果:")
    for vehicle in sorted(mappings.keys()):
        print(f"\n{vehicle}:")
        for button_id, io_index in sorted(mappings[vehicle].items(), key=lambda x: x[1]):
            print(f"  {button_id}: {io_index}")
    
    # 更新config.py
    print("\n开始更新config.py...")
    update_config_file(mappings)
    print("完成！")
