# -*- coding: utf-8 -*-
"""
检查并修复缺失的按钮映射
"""
import sys
sys.path.insert(0, '.')

from test_data.button_test import BUTTON_TEST_DATA
import config

def check_and_fix():
    """检查所有测试项是否都有IO映射，并生成修复建议"""
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
            print(f"\n{vehicle}: 所有按钮都有映射")
    
    # 如果发现缺失，提供修复建议
    if all_missing:
        print("\n" + "="*50)
        print("修复建议:")
        print("="*50)
        print("\n根据CSV文件，以下按钮在某些车型中可能不存在或未定义IO映射。")
        print("如果这些按钮在硬件上存在，需要更新CSV文件或手动补充配置。")
        print("\n缺失的映射:")
        for vehicle, missing in all_missing.items():
            print(f"\n{vehicle}:")
            for btn_id in missing:
                # 根据按钮ID推断可能的IO索引
                print(f"  - {btn_id}: 需要确认IO索引")
        return False
    else:
        print("\n" + "="*50)
        print("所有车型的按键测试项都已匹配完成！")
        print("="*50)
        return True

if __name__ == '__main__':
    success = check_and_fix()
    sys.exit(0 if success else 1)
