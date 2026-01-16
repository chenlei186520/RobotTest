# -*- coding: utf-8 -*-
"""
解析devices_data.csv文件
"""
import csv

# 尝试不同的编码
encodings = ['utf-8', 'gbk', 'gb2312', 'utf-8-sig']

def parse_csv():
    file_path = 'test_data/devices_data.csv'
    
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
        print("无法读取文件")
        return
    
    # 解析CSV
    import io
    reader = csv.reader(io.StringIO(content))
    rows = list(reader)
    
    print("=" * 80)
    print("CSV文件解析结果")
    print("=" * 80)
    print(f"文件编码: {used_encoding}")
    print(f"总行数: {len(rows)}\n")
    
    # 显示表头
    if len(rows) > 0:
        print("表头:")
        headers = rows[0]
        for i, header in enumerate(headers, 1):
            print(f"  列{i}: {header}")
    
    # 解析数据
    print("\n" + "=" * 80)
    print("详细数据:")
    print("=" * 80)
    
    x060_data = {}
    x150_data = {}
    
    for i, row in enumerate(rows[1:], start=1):
        if len(row) >= 5:
            io_index = row[0].strip()
            x060_name = row[1].strip() if len(row) > 1 else ""
            x060_desc = row[2].strip() if len(row) > 2 else ""
            x150_name = row[3].strip() if len(row) > 3 else ""
            x150_desc = row[4].strip() if len(row) > 4 else ""
            
            if io_index and io_index.isdigit():
                io_idx = int(io_index)
                print(f"\n行{i+1} - IO索引 {io_idx}:")
                
                if x060_name:
                    print(f"  X060/X080: {x060_name}")
                    if x060_desc:
                        print(f"    说明: {x060_desc}")
                    if io_idx not in x060_data:
                        x060_data[io_idx] = []
                    x060_data[io_idx].append(x060_name)
                
                if x150_name:
                    print(f"  X150/X100: {x150_name}")
                    if x150_desc:
                        print(f"    说明: {x150_desc}")
                    if io_idx not in x150_data:
                        x150_data[io_idx] = []
                    x150_data[io_idx].append(x150_name)
    
    # 汇总映射
    print("\n" + "=" * 80)
    print("映射汇总:")
    print("=" * 80)
    
    print("\n【X060/X080车型】")
    print("-" * 80)
    for io_idx in sorted(x060_data.keys()):
        items = x060_data[io_idx]
        print(f"IO索引 {io_idx:2d}: {', '.join(items)}")
    
    print("\n【X150/X100车型】")
    print("-" * 80)
    for io_idx in sorted(x150_data.keys()):
        items = x150_data[io_idx]
        print(f"IO索引 {io_idx:2d}: {', '.join(items)}")
    
    print("\n" + "=" * 80)
    print("解析完成！")
    print("=" * 80)

if __name__ == '__main__':
    parse_csv()
