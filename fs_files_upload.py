import requests
import json
import os
from requests_toolbelt import MultipartEncoder


# -------------------------- 第一步：获取tenant_access_token --------------------------
# 飞书云文档地址 ： https://thundersoft.feishu.cn/drive/folder/K5RAfwXaNl0Mc2dmp5dcpmFinKb
def get_tenant_access_token(app_id: str, app_secret: str):
    """
    调用飞书接口获取tenant_access_token
    :param app_id: 飞书应用ID
    :param app_secret: 飞书应用秘钥
    :return: 成功返回tenant_access_token，失败返回None
    """
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    headers = {
        "Content-Type": "application/json; charset=utf-8"  # 飞书要求的固定请求头
    }
    request_body = {
        "app_id": app_id,
        "app_secret": app_secret
    }

    try:
        # 发送POST请求获取token
        response = requests.post(
            url=url,
            headers=headers,
            data=json.dumps(request_body),
            timeout=10
        )
        response.raise_for_status()  # 捕获HTTP状态码错误
        result = response.json()

        # 校验返回结果
        if result.get("code") == 0 and result.get("tenant_access_token"):
            tenant_access_token = result["tenant_access_token"]
            expire = result["expire"]
            print(f"[成功] 获取tenant_access_token成功，有效期{expire}秒")
            return tenant_access_token
        else:
            print(f"[失败] 获取token失败：{result.get('msg', '未知错误')}，错误码：{result.get('code')}")
            return None

    except requests.exceptions.Timeout:
        print("[失败] 请求超时：连接飞书服务器超时，请检查网络")
        return None
    except requests.exceptions.ConnectionError:
        print("[失败] 连接失败：无法连接到飞书服务器")
        return None
    except json.JSONDecodeError:
        print("[失败] 解析失败：飞书返回非JSON格式数据")
        return None
    except Exception as e:
        print(f"[失败] 获取token未知错误：{str(e)}")
        return None


# -------------------------- 第二步：上传文件到飞书云文档 --------------------------
def upload_file(tenant_access_token: str, cloudname: str, cloudsize: int, file_path: str = None):
    """
    上传文件到飞书云文档指定文件夹
    :param tenant_access_token: 飞书租户token
    :param cloudname: 上传后的文件名
    :param cloudsize: 文件大小（字节）
    :param file_path: 文件路径（如果为None，则使用默认路径）
    """
    # 校验token是否有效
    if not tenant_access_token:
        print("[失败] token为空，无法上传文件")
        return

    # 构造文件路径
    if file_path is None:
        # 获取脚本所在目录
        script_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(script_dir, 'report', cloudname)
    
    # 校验文件是否存在
    if not os.path.exists(file_path):
        print(f"[失败] 文件不存在：{file_path}")
        return

    # 飞书文件上传接口
    url = "https://open.feishu.cn/open-apis/drive/v1/files/upload_all"

    # 构造表单数据
    try:
        form = {
            'file_name': cloudname,
            'parent_type': 'explorer',  # 上传到云文档资源管理器
            'parent_node': 'K5RAfwXaNl0Mc2dmp5dcpmFinKb',  # 目标文件夹ID
            'size': str(cloudsize),  # 文件大小（字符串格式）
            'file': (cloudname, open(file_path, 'rb'), 'application/octet-stream')  # 补充文件MIME类型
        }
        multi_form = MultipartEncoder(form)

        # 构造请求头（包含token和自动生成的Content-Type）
        headers = {
            'Authorization': f'Bearer {tenant_access_token}',
            'Content-Type': multi_form.content_type
        }

        # 发送上传请求
        print(f"[上传] 开始上传文件：{file_path}")
        response = requests.post(
            url=url,
            headers=headers,
            data=multi_form,
            timeout=30  # 上传文件超时时间设长一点
        )
        response.raise_for_status()
        result = response.json()

        # 处理上传结果
        if result.get("code") == 0:
            print(f"[成功] 文件上传成功！文件ID：{result.get('data', {}).get('file_token')}")
            print(f"[详情] 响应详情：{json.dumps(result, indent=4, ensure_ascii=False)}")
        else:
            print(f"[失败] 文件上传失败：{result.get('msg', '未知错误')}，错误码：{result.get('code')}")

    except requests.exceptions.Timeout:
        print("[失败] 文件上传超时：请检查网络或文件大小")
    except requests.exceptions.ConnectionError:
        print("[失败] 文件上传连接失败")
    except Exception as e:
        print(f"[失败] 文件上传未知错误：{str(e)}")
    finally:
        # 确保文件句柄关闭
        if 'file' in form and form['file'][1]:
            form['file'][1].close()


# -------------------------- 主函数：整合调用 --------------------------
if __name__ == '__main__':
    import sys
    
    # -------------------------- 配置项（替换为你的实际值） --------------------------
    FEISHU_APP_ID = "cli_a9ef50b1697a9cb2"  # 你的飞书应用ID
    FEISHU_APP_SECRET = "90VEVYBWa4YY16A2XZXo5eQspbZnVm24"  # 你的飞书应用秘钥
    
    # 从命令行参数获取文件名和大小
    if len(sys.argv) >= 3:
        CLOUD_NAME = sys.argv[1]  # 文件名（含后缀）
        CLOUD_SIZE = int(sys.argv[2])  # 文件大小（字节）
        print(f"[参数] 接收参数: cloudname={CLOUD_NAME}, cloudsize={CLOUD_SIZE}")
    else:
        # 如果没有参数，使用默认值（用于测试）
        CLOUD_NAME = "机器人静态测试报告_X-080-V1-CE-LV-2L-C-1A-V1.1_20260113.xlsx"
        CLOUD_SIZE = 6100
        print("[警告] 未提供命令行参数，使用默认值")
    
    # 1. 获取tenant_access_token
    token = get_tenant_access_token(FEISHU_APP_ID, FEISHU_APP_SECRET)

    # 2. 上传文件
    if token:
        upload_file(
            tenant_access_token=token,
            cloudname=CLOUD_NAME,
            cloudsize=CLOUD_SIZE
        )
    else:
        print("[终止] 未获取到有效token，终止文件上传")