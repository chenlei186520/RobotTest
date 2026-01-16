# -*- coding: utf-8 -*-
"""
检查并转换CSV文件编码为UTF-8
"""
import sys

def check_encoding(file_path):
    """检查文件编码"""
    encodings = ['utf-8', 'gbk', 'gb2312', 'utf-8-sig', 'latin-1']
    
    print(f"检查文件: {file_path}")
    print("=" * 60)
    
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
                # 尝试读取前几行
                lines = content.split('\n')[:3]
                print(f"\n使用 {encoding} 编码读取成功:")
                for i, line in enumerate(lines, 1):
                    print(f"  行{i}: {line[:50]}...")
                return encoding, content
        except UnicodeDecodeError as e:
            print(f"\n使用 {encoding} 编码读取失败: {e}")
        except Exception as e:
            print(f"\n使用 {encoding} 编码读取出错: {e}")
    
    return None, None

def convert_to_utf8(file_path, source_encoding=None):
    """将文件转换为UTF-8格式"""
    print("\n" + "=" * 60)
    print("转换文件为UTF-8格式")
    print("=" * 60)
    
    # 先检查当前编码
    if source_encoding:
        try:
            with open(file_path, 'r', encoding=source_encoding) as f:
                content = f.read()
        except:
            # 如果指定编码失败，尝试自动检测
            encodings = ['utf-8', 'gbk', 'gb2312', 'utf-8-sig']
            for enc in encodings:
                try:
                    with open(file_path, 'r', encoding=enc) as f:
                        content = f.read()
                    source_encoding = enc
                    print(f"自动检测到编码: {enc}")
                    break
                except:
                    continue
    else:
        # 尝试自动检测
        encodings = ['utf-8', 'gbk', 'gb2312', 'utf-8-sig']
        for enc in encodings:
            try:
                with open(file_path, 'r', encoding=enc) as f:
                    content = f.read()
                source_encoding = enc
                print(f"自动检测到编码: {enc}")
                break
            except:
                continue
    
    if not content:
        print("无法读取文件内容")
        return False
    
    # 保存为UTF-8格式（不带BOM）
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"\n[成功] 文件已成功转换为UTF-8格式")
        print(f"  源编码: {source_encoding}")
        print(f"  目标编码: utf-8")
        return True
    except Exception as e:
        print(f"\n[失败] 转换失败: {e}")
        return False

if __name__ == '__main__':
    file_path = 'test_data/devices_data.csv'
    
    # 检查编码
    encoding, content = check_encoding(file_path)
    
    if encoding:
        print(f"\n当前文件编码: {encoding}")
        
        if encoding.lower() not in ['utf-8', 'utf-8-sig']:
            print("\n文件不是UTF-8格式，开始转换...")
            convert_to_utf8(file_path, encoding)
        else:
            print("\n文件已经是UTF-8格式，无需转换")
    else:
        print("\n无法确定文件编码，尝试转换...")
        convert_to_utf8(file_path)
    
    # 再次验证
    print("\n" + "=" * 60)
    print("验证转换结果")
    print("=" * 60)
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            print(f"[成功] 使用UTF-8编码成功读取文件")
            print(f"  总行数: {len(lines)}")
            print(f"  前3行内容:")
            for i, line in enumerate(lines[:3], 1):
                print(f"    行{i}: {line.strip()[:60]}")
    except Exception as e:
        print(f"[失败] UTF-8读取失败: {e}")
