# -*- coding: utf-8 -*-
"""
安全解析devices_data.csv文件（支持多种编码）
"""
import csv
import sys

def parse_csv_file(file_path):
    """解析CSV文件并显示内容"""
    # 尝试不同的编码
    encodings = ['utf-8', 'gbk', 'gb2312', 'utf-8-sig', 'latin-1']
    
    content = None
    used_encoding = None
    
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
                used_encoding = encoding
                print(f"成功使用 {encoding} 编码读取文件\n")
                break
        except Exception as e:
            continue
    
    if not content:
        print("无法读取文件，尝试了所有编码格式")
        return
    
    # 解析CSV
    import io
    reader = csv.reader(io.StringIO(content))
    rows = list(reader)
    
    print("=" * 80)
    print("CSV文件解析报告")
    print("=" * 80)
    print(f"文件: {file_path}")
    print(f"编码: {used_encoding}")
    print(f"总行数: {len(rows)}\n")
    
    # 显示表头
    if len(rows) > 0:
        print("表头:")
        for i, header in enumerate(rows[0], 1):
            print(f"  列{i}: {header}")
    
    # 解析数据
    print("\n" + "=" * 80)
    print("数据映射关系:")
    print("=" * 80)
    
    x060_mapping = {}  # {io_index: [按钮名称列表]}
    x150_mapping = {}  # {io_index: [按钮名称列表]}
    
    for i, row in enumerate(rows[1:], start=1):
        if len(row) >= 5:
            io_index_str = row[0].strip()
            x060_name = row[1].strip() if len(row) > 1 else ""
            x060_desc = row[2].strip() if len(row) > 2 else ""
            x150_name = row[3].strip() if len(row) > 3 else ""
            x150_desc = row[4].strip() if len(row) > 4 else ""
            
            if io_index_str and io_index_str.isdigit():
                io_index = int(io_index_str)
                
                # 解析X060/X080
                if x060_name:
                    # 处理多个按钮（用空格分隔）
                    buttons = [b.strip() for b in x060_name.split() if b.strip()]
                    if io_index not in x060_mapping:
                        x060_mapping[io_index] = []
                    x060_mapping[io_index].extend(buttons)
                
                # 解析X150/X100
                if x150_name:
                    # 处理多个按钮（用空格分隔）
                    buttons = [b.strip() for b in x150_name.split() if b.strip()]
                    if io_index not in x150_mapping:
                        x150_mapping[io_index] = []
                    x150_mapping[io_index].extend(buttons)
    
    # 显示X060/X080映射
    print("\n【X060/X080车型映射】")
    print("-" * 80)
    for io_index in sorted(x060_mapping.keys()):
        buttons = x060_mapping[io_index]
        print(f"IO索引 {io_index:2d}: {', '.join(buttons)}")
    
    # 显示X150/X100映射
    print("\n【X150/X100车型映射】")
    print("-" * 80)
    for io_index in sorted(x150_mapping.keys()):
        buttons = x150_mapping[io_index]
        print(f"IO索引 {io_index:2d}: {', '.join(buttons)}")
    
    # 统计信息
    print("\n" + "=" * 80)
    print("统计信息:")
    print("=" * 80)
    print(f"X060/X080: 共 {len(x060_mapping)} 个IO索引有映射")
    print(f"X150/X100: 共 {len(x150_mapping)} 个IO索引有映射")
    
    # 检查缺失的按钮
    print("\n" + "=" * 80)
    print("按键测试项检查:")
    print("=" * 80)
    
    # 按键测试中需要的所有按钮ID
    required_buttons = {
        'front_right_confirm': '右前确认按钮',
        'back_right_confirm': '右后确认按钮',
        'front_right_maintenance': '右前维修按钮',
        'back_right_maintenance': '右后维修按钮',
        'front_right_emergency': '右前急停按钮',
        'back_right_emergency': '右后急停按钮',
        'front_left_emergency': '左前急停按钮',
        'back_left_emergency': '左后急停按钮'
    }
    
    # 按钮名称到ID的映射规则
    def name_to_id(name):
        name_clean = name.replace('（需要按一段时间）', '').replace('键', '').replace('（', '').replace('）', '')
        if '右前确认' in name_clean:
            return 'front_right_confirm'
        elif '右后确认' in name_clean:
            return 'back_right_confirm'
        elif '右前维护' in name_clean or '右前维修' in name_clean:
            return 'front_right_maintenance'
        elif '右后维护' in name_clean or '右后维修' in name_clean:
            return 'back_right_maintenance'
        elif '右前急停' in name_clean:
            return 'front_right_emergency'
        elif '右后急停' in name_clean:
            return 'back_right_emergency'
        elif '左前急停' in name_clean:
            return 'front_left_emergency'
        elif '左后急停' in name_clean:
            return 'back_left_emergency'
        return None
    
    # 检查X060/X080
    x060_found = set()
    for io_index, buttons in x060_mapping.items():
        for button_name in buttons:
            btn_id = name_to_id(button_name)
            if btn_id:
                x060_found.add(btn_id)
    
    print("\nX060/X080车型:")
    missing_x060 = set(required_buttons.keys()) - x060_found
    if missing_x060:
        print(f"  缺失的按钮: {', '.join([required_buttons[b] for b in missing_x060])}")
    else:
        print("  [OK] 所有按钮都有映射")
    print(f"  已映射的按钮: {', '.join([required_buttons[b] for b in sorted(x060_found)])}")
    
    # 检查X150/X100
    x150_found = set()
    for io_index, buttons in x150_mapping.items():
        for button_name in buttons:
            btn_id = name_to_id(button_name)
            if btn_id:
                x150_found.add(btn_id)
    
    print("\nX150/X100车型:")
    missing_x150 = set(required_buttons.keys()) - x150_found
    if missing_x150:
        print(f"  缺失的按钮: {', '.join([required_buttons[b] for b in missing_x150])}")
    else:
        print("  [OK] 所有按钮都有映射")
    print(f"  已映射的按钮: {', '.join([required_buttons[b] for b in sorted(x150_found)])}")
    
    # 生成配置建议
    print("\n" + "=" * 80)
    print("配置建议:")
    print("=" * 80)
    
    print("\nX060/X080配置:")
    for io_index in sorted(x060_mapping.keys()):
        buttons = x060_mapping[io_index]
        for button_name in buttons:
            btn_id = name_to_id(button_name)
            if btn_id:
                print(f"  \"{btn_id}\": {io_index},  # {button_name}")
    
    print("\nX150/X100配置:")
    for io_index in sorted(x150_mapping.keys()):
        buttons = x150_mapping[io_index]
        for button_name in buttons:
            btn_id = name_to_id(button_name)
            if btn_id:
                print(f"  \"{btn_id}\": {io_index},  # {button_name}")
    
    print("\n" + "=" * 80)
    print("解析完成！")
    print("=" * 80)

if __name__ == '__main__':
    parse_csv_file('test_data/devices_data.csv')
