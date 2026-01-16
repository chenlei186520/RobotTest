# 举升电机测试API处理器

from .base_api import BaseAPI
import config
import requests

class LiftMotorAPI(BaseAPI):
    """举升电机测试专用的API处理器"""
    
    @staticmethod
    def send_command(item_id, ssh_host=None, ssh_user=None, ssh_password=None, height=None):
        """发送举升电机控制指令（通过HTTP接口）
        
        Args:
            item_id: 测试项ID ('lift_up' 或 'lift_down')
            ssh_host: 设备IP地址（用于HTTP请求）
            ssh_user: SSH用户名（未使用，保留兼容性）
            ssh_password: SSH密码（未使用，保留兼容性）
            height: 举升高度（整数），传入liftHeight参数
        """
        # 从ssh_host获取IP地址，用于HTTP请求
        if not ssh_host:
            return {"status": "error", "message": "未提供设备IP地址"}
        
        # 放下操作：固定使用高度0
        if item_id == 'lift_down':
            lift_height = 0
            print(f"[举升电机测试] 放下操作：固定使用高度0")
        else:
            # 举升操作：从参数获取高度
            if not height:
                return {"status": "error", "message": "未提供举升高度"}
            
            try:
                lift_height = int(height)
            except (ValueError, TypeError):
                return {"status": "error", "message": f"举升高度必须是整数，当前值: {height}"}
        
        # 构建HTTP接口URL（使用ssh_host作为IP地址，端口10086）
        api_url = f"http://{ssh_host}:10086/api/TrayControl"
        
        # 构建请求数据
        request_data = {
            "cmd": 2,
            "liftHeight": lift_height
        }
        
        try:
            # 发送HTTP POST请求
            print(f"[举升电机测试] ========== HTTP请求信息 ==========")
            print(f"[举升电机测试] 请求接口: {api_url}")
            print(f"[举升电机测试] 请求方法: POST")
            print(f"[举升电机测试] 请求数据: {request_data}")
            print(f"[举升电机测试] 举升高度(liftHeight): {lift_height} (类型: {type(lift_height).__name__})")
            print(f"[举升电机测试] ====================================")
            
            response = requests.post(
                api_url,
                json=request_data,
                timeout=10  # 10秒超时
            )
            
            # 检查HTTP状态码
            print(f"[举升电机测试] HTTP响应状态码: {response.status_code}")
            response_text = response.text.strip()
            print(f"[举升电机测试] HTTP响应数据: {response_text}")
            
            if response.status_code == 200:
                print(f"[举升电机测试] ✅ 举升电机控制指令发送成功")
                return {"status": "success", "message": "举升电机控制指令发送成功"}
            else:
                print(f"[举升电机测试] ❌ HTTP请求失败，状态码: {response.status_code}")
                return {"status": "error", "message": f"HTTP请求失败，状态码: {response.status_code}, 响应: {response.text[:200]}"}
        
        except requests.exceptions.Timeout:
            return {"status": "error", "message": "HTTP请求超时"}
        except requests.exceptions.ConnectionError:
            return {"status": "error", "message": f"无法连接到设备 {ssh_host}:10086，请检查网络连接"}
        except requests.exceptions.RequestException as e:
            return {"status": "error", "message": f"HTTP请求异常: {str(e)}"}
        except Exception as e:
            return {"status": "error", "message": f"发送举升电机控制指令失败: {str(e)}"}
    
    @staticmethod
    def check_io(item_id):
        """检查举升电机IO状态（如果需要）"""
        # 举升电机测试需要人工测量，不需要IO检查
        return {"status": "success", "message": "举升电机测试需要人工测量，无需IO检查"}
