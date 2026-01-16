# -*- coding: utf-8 -*-
"""
检查按键测试项是否都已匹配IO映射
"""
import sys
sys.path.insert(0, '.')

from test_data.button_test import BUTTON_TEST_DATA
import config

def check_mapping():
    """检查所有测试项是否都有IO映射"""
    # 获取所有按钮ID
    all_button_ids = set()
    for section in BUTTON_TEST_DATA['sections']:
        for item in section['items']:
            all_button_ids.add(item['id'])
    
    print("按键测试中定义的所有按钮ID:")
    for button_id in sorted(all_button_ids):
        print(f"  - {button_id}")
    
    print("\n检查各车型的映射情况:")
    
    # 检查每个车型
    vehicles = ['X060', 'X080', 'X100', 'X150']
    all_missing = {}
    
    for vehicle in vehicles:
        io_map = config.get_button_io_map(vehicle)
        missing = []
        for button_id in all_button_ids:
            if button_id not in io_map:
                missing.append(button_id)
        
        if missing:
            all_missing[vehicle] = missing
            print(f"\n{vehicle} 缺少映射的按钮:")
            for btn_id in missing:
                print(f"  - {btn_id}")
        else:
            print(f"\n{vehicle}: ✓ 所有按钮都有映射")
            print(f"  映射详情:")
            for btn_id in sorted(io_map.keys()):
                print(f"    {btn_id}: IO索引{io_map[btn_id]}")
    
    return all_missing

if __name__ == '__main__':
    missing = check_mapping()
    if missing:
        print("\n⚠️ 发现缺失的映射，需要检查CSV文件或补充配置")
    else:
        print("\n✓ 所有车型的按键测试项都已匹配完成！")
