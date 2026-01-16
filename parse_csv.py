# -*- coding: utf-8 -*-
"""
解析devices_data.csv文件
"""
import csv

def parse_csv_file(file_path):
    """解析CSV文件并显示内容"""
    print(f"正在解析文件: {file_path}")
    print("=" * 80)
    
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        rows = list(reader)
    
    print(f"总行数: {len(rows)}\n")
    
    # 显示表头
    if len(rows) > 0:
        print("表头:")
        print(f"  {rows[0]}\n")
    
    # 解析数据
    print("数据内容:")
    print("-" * 80)
    
    for i, row in enumerate(rows[1:], start=1):
        if len(row) >= 5:
            io_index = row[0].strip()
            x060_name = row[1].strip() if len(row) > 1 else ""
            x060_desc = row[2].strip() if len(row) > 2 else ""
            x150_name = row[3].strip() if len(row) > 3 else ""
            x150_desc = row[4].strip() if len(row) > 4 else ""
            
            if io_index and io_index.isdigit():
                print(f"\nIO索引 {io_index}:")
                if x060_name:
                    print(f"  X060/X080: {x060_name}")
                    if x060_desc:
                        print(f"    含义: {x060_desc}")
                if x150_name:
                    print(f"  X150/X100: {x150_name}")
                    if x150_desc:
                        print(f"    含义: {x150_desc}")
    
    print("\n" + "=" * 80)
    print("\n解析完成！")

if __name__ == '__main__':
    parse_csv_file('test_data/devices_data.csv')
