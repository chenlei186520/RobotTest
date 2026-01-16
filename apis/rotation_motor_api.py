# 旋转电机测试API处理器

from .base_api import BaseAPI
import config
import requests

class RotationMotorAPI(BaseAPI):
    """旋转电机测试专用的API处理器"""
    
    @staticmethod
    def send_command(item_id, ssh_host=None, ssh_user=None, ssh_password=None, angle=None):
        """发送旋转电机控制指令（通过HTTP接口）
        
        Args:
            item_id: 测试项ID ('rotate' 或 'reset')
            ssh_host: 设备IP地址（用于HTTP请求）
            ssh_user: SSH用户名（未使用，保留兼容性）
            ssh_password: SSH密码（未使用，保留兼容性）
            angle: 旋转/归零角度（整数），传入angle参数
        """
        # 从ssh_host获取IP地址，用于HTTP请求
        if not ssh_host:
            return {"status": "error", "message": "未提供设备IP地址"}
        
        # 归零操作：固定使用角度0
        if item_id == 'reset':
            rotation_angle = 0
            print(f"[旋转电机测试] 归零操作：固定使用角度0")
        else:
            # 旋转操作：从参数获取角度
            if angle is None:
                return {"status": "error", "message": "未提供旋转角度"}
            
            try:
                rotation_angle = int(angle)
            except (ValueError, TypeError):
                return {"status": "error", "message": f"角度必须是整数，当前值: {angle}"}
        
        # 构建HTTP接口URL（使用ssh_host作为IP地址，端口10086）
        api_url = f"http://{ssh_host}:10086/api/TrayControl"
        
        # 构建请求数据
        request_data = {
            "cmd": 3,
            "angle": rotation_angle
        }
        
        try:
            # 发送HTTP POST请求
            print(f"[旋转电机测试] ========== HTTP请求信息 ==========")
            print(f"[旋转电机测试] 请求接口: {api_url}")
            print(f"[旋转电机测试] 请求方法: POST")
            print(f"[旋转电机测试] 请求数据: {request_data}")
            print(f"[旋转电机测试] 旋转/归零角度(angle): {rotation_angle} (类型: {type(rotation_angle).__name__})")
            print(f"[旋转电机测试] 动作类型(item_id): {item_id}")
            print(f"[旋转电机测试] ====================================")
            
            response = requests.post(
                api_url,
                json=request_data,
                timeout=10  # 10秒超时
            )
            
            # 检查HTTP状态码
            print(f"[旋转电机测试] HTTP响应状态码: {response.status_code}")
            response_text = response.text.strip()
            print(f"[旋转电机测试] HTTP响应数据: {response_text}")
            
            if response.status_code == 200:
                print(f"[旋转电机测试] ✅ 旋转电机控制指令发送成功")
                return {"status": "success", "message": "旋转电机控制指令发送成功"}
            else:
                print(f"[旋转电机测试] ❌ HTTP请求失败，状态码: {response.status_code}")
                return {"status": "error", "message": f"HTTP请求失败，状态码: {response.status_code}, 响应: {response.text[:200]}"}
        
        except requests.exceptions.Timeout:
            return {"status": "error", "message": "HTTP请求超时"}
        except requests.exceptions.ConnectionError:
            return {"status": "error", "message": f"无法连接到设备 {ssh_host}:10086，请检查网络连接"}
        except requests.exceptions.RequestException as e:
            return {"status": "error", "message": f"HTTP请求异常: {str(e)}"}
        except Exception as e:
            return {"status": "error", "message": f"发送旋转电机控制指令失败: {str(e)}"}
    
    @staticmethod
    def check_io(item_id):
        """检查旋转电机IO状态（如果需要）"""
        # 旋转电机测试需要人工测量，不需要IO检查
        return {"status": "success", "message": "旋转电机测试需要人工测量，无需IO检查"}
