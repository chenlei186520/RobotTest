# 行走电机测试API处理器

from .base_api import BaseAPI
import config
import requests

class WalkingMotorAPI(BaseAPI):
    """行走电机测试专用的API处理器"""
    
    @staticmethod
    def send_command(item_id, ssh_host=None, ssh_user=None, ssh_password=None, distance=None):
        """发送行走电机控制指令（通过HTTP接口）
        
        Args:
            item_id: 测试项ID ('forward' 或 'backward')
            ssh_host: 设备IP地址（用于HTTP请求）
            ssh_user: SSH用户名（未使用，保留兼容性）
            ssh_password: SSH密码（未使用，保留兼容性）
            distance: 移动距离（米），传入distance参数
        """
        # 从ssh_host获取IP地址，用于HTTP请求
        if not ssh_host:
            return {"status": "error", "message": "未提供设备IP地址"}
        
        # 将距离转换为浮点数
        if distance is None:
            return {"status": "error", "message": "未提供移动距离"}
        
        try:
            move_distance = float(distance)
        except (ValueError, TypeError):
            return {"status": "error", "message": f"距离必须是数字，当前值: {distance}"}
        
        # 根据动作类型设置cmd值：前进=0，后退=1
        if item_id == 'forward':
            cmd_value = 0
            action_name = '前进'
        elif item_id == 'backward':
            cmd_value = 1
            action_name = '后退'
        else:
            return {"status": "error", "message": f"未知的动作类型: {item_id}"}
        
        # 构建HTTP接口URL（使用ssh_host作为IP地址，端口10086）
        api_url = f"http://{ssh_host}:10086/api/CarMoveControl"
        
        # 构建请求数据
        request_data = {
            "cmd": cmd_value,
            "distance": move_distance,
            "speed": 0.5
        }
        
        try:
            # 发送HTTP POST请求
            print(f"[行走电机测试] ========== HTTP请求信息 ==========")
            print(f"[行走电机测试] 请求接口: {api_url}")
            print(f"[行走电机测试] 请求方法: POST")
            print(f"[行走电机测试] 请求数据: {request_data}")
            print(f"[行走电机测试] 移动距离(distance): {move_distance}米 (类型: {type(move_distance).__name__})")
            print(f"[行走电机测试] 动作类型(item_id): {item_id} ({action_name})")
            print(f"[行走电机测试] 命令值(cmd): {cmd_value}")
            print(f"[行走电机测试] ====================================")
            
            response = requests.post(
                api_url,
                json=request_data,
                timeout=10  # 10秒超时
            )
            
            # 检查HTTP状态码
            print(f"[行走电机测试] HTTP响应状态码: {response.status_code}")
            response_text = response.text.strip()
            print(f"[行走电机测试] HTTP响应数据: {response_text}")
            
            if response.status_code == 200:
                print(f"[行走电机测试] ✅ 行走电机控制指令发送成功")
                return {"status": "success", "message": "行走电机控制指令发送成功"}
            else:
                print(f"[行走电机测试] ❌ HTTP请求失败，状态码: {response.status_code}")
                return {"status": "error", "message": f"HTTP请求失败，状态码: {response.status_code}, 响应: {response.text[:200]}"}
        
        except requests.exceptions.Timeout:
            return {"status": "error", "message": "HTTP请求超时"}
        except requests.exceptions.ConnectionError:
            return {"status": "error", "message": f"无法连接到设备 {ssh_host}:10086，请检查网络连接"}
        except requests.exceptions.RequestException as e:
            return {"status": "error", "message": f"HTTP请求异常: {str(e)}"}
        except Exception as e:
            return {"status": "error", "message": f"发送行走电机控制指令失败: {str(e)}"}
    
    @staticmethod
    def check_io(item_id):
        """检查行走电机IO状态（如果需要）"""
        # 行走电机测试需要人工测量，不需要IO检查
        return {"status": "success", "message": "行走电机测试需要人工测量，无需IO检查"}
