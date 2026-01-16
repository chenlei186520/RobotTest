# 语音测试API处理器

from .base_api import BaseAPI
import config
import requests

class VoiceAPI(BaseAPI):
    """语音测试专用的API处理器"""
    
    @staticmethod
    def send_command(item_id, ssh_host=None, ssh_user=None, ssh_password=None):
        """发送语音控制指令（通过HTTP接口）"""
        if item_id != 'voice_broadcast':
            return {"status": "error", "message": "未知的语音测试项"}
        
        # 从ssh_host获取IP地址，用于HTTP请求
        if not ssh_host:
            return {"status": "error", "message": "未提供设备IP地址"}
        
        # 语音测试完整流程：
        # 1. 发送SSH指令 rosnode kill /task_manager
        # 2. 等待20秒
        # 3. 执行HTTP请求
        # 4. 等待2秒
        # 5. 执行SSH指令 roslaunch task_manager task_manager.launch &
        # 6. 等待10秒
        
        ssh_user = ssh_user or config.SSH_USER
        ssh_password = ssh_password or config.SSH_PASSWORD
        
        import paramiko
        import time
        
        ssh = None  # 初始化SSH连接变量
        
        # 步骤1: 执行 rosnode kill /task_manager
        try:
            print(f"[语音测试] 步骤1: 正在通过SSH执行命令: rosnode kill /task_manager")
            
            # 建立SSH连接
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(
                hostname=ssh_host,
                port=22,
                username=ssh_user,
                password=ssh_password,
                timeout=10,
                allow_agent=False,
                look_for_keys=False
            )
            
            # 执行 rosnode kill /task_manager 命令
            # 需要先source ROS环境，因为exec_command不会自动加载环境变量
            # 尝试多个可能的ROS环境路径（使用bash -c确保shell正确执行）
            command = "bash -c 'source /opt/ros/melodic/setup.bash 2>/dev/null || source /opt/ros/noetic/setup.bash 2>/dev/null || source ~/catkin_ws/devel/setup.bash 2>/dev/null || source $(find /opt/ros -name setup.bash 2>/dev/null | head -1) 2>/dev/null; rosnode kill /task_manager'"
            stdin, stdout, stderr = ssh.exec_command(command, timeout=10)
            
            # 等待命令执行完成
            exit_status = stdout.channel.recv_exit_status()
            output = stdout.read().decode('utf-8', errors='ignore')
            error_output = stderr.read().decode('utf-8', errors='ignore')
            
            print(f"[语音测试] SSH命令执行完成，退出状态: {exit_status}")
            if output:
                print(f"[语音测试] SSH命令输出: {output.strip()}")
            if error_output:
                print(f"[语音测试] SSH命令错误输出: {error_output.strip()}")
            
            # 注意：即使rosnode kill命令失败（节点不存在），也继续执行后续步骤
            # 因为节点可能已经不存在，这是正常情况
            # 不关闭SSH连接，等待20秒后可能还需要使用（但20秒后连接可能超时，步骤5会重新建立）
            
        except paramiko.AuthenticationException as e:
            print(f"[语音测试] ⚠️ SSH认证失败，继续执行后续步骤: {e}")
            ssh = None
        except paramiko.SSHException as e:
            print(f"[语音测试] ⚠️ SSH连接错误，继续执行后续步骤: {e}")
            ssh = None
        except Exception as e:
            print(f"[语音测试] ⚠️ SSH命令执行异常，继续执行后续步骤: {e}")
            ssh = None
        
        # 步骤2: 等待20秒
        print(f"[语音测试] 步骤2: 等待20秒...")
        time.sleep(20)
        print(f"[语音测试] 等待完成，发送Ctrl+C操作")
        
        # 等待20秒后，发送Ctrl+C操作
        try:
            if ssh and ssh.get_transport() and ssh.get_transport().is_active():
                # 创建交互式shell通道来发送Ctrl+C
                channel = ssh.invoke_shell()
                channel.send(b'\x03')  # Ctrl+C (ASCII码3)
                time.sleep(0.5)  # 短暂等待
                channel.close()
                print(f"[语音测试] Ctrl+C操作已发送（步骤2后）")
        except Exception as e:
            print(f"[语音测试] ⚠️ 发送Ctrl+C操作失败（步骤2后）: {e}")
        
        print(f"[语音测试] 开始执行HTTP请求")
        
        # 构建HTTP接口URL（使用ssh_host作为IP地址，端口10086）
        api_url = f"http://{ssh_host}:10086/api/LightAndAudio"
        
        # 构建请求数据
        request_data = {
            "dtc": "0",
            "status": 6,
            "warningType": 3
        }
        
        # 步骤3: 执行HTTP请求
        http_success = False
        http_message = ""
        
        try:
            # 发送HTTP POST请求
            print(f"[语音测试] 步骤3: 发送HTTP请求到: {api_url}")
            print(f"[语音测试调试] 请求数据: {request_data}")
            
            response = requests.post(
                api_url,
                json=request_data,
                timeout=10  # 10秒超时
            )
            
            # 检查HTTP状态码
            if response.status_code == 200:
                # 获取原始响应文本
                response_text = response.text.strip()
                print(f"[语音测试调试] 原始返回数据: {response_text}")
                
                # 直接检查响应文本中是否包含"true"（不进行严格JSON解析）
                # 支持多种格式：{"Result": true}、{"Result":true}、"Result" : true等
                if '"Result"' in response_text or "'Result'" in response_text:
                    # 检查Result是否为true
                    if '"Result" : true' in response_text or '"Result":true' in response_text or '"Result": true' in response_text or "'Result' : true" in response_text or "'Result':true" in response_text:
                        print(f"[语音测试调试] 检测到Result为true，语音播报成功")
                        http_success = True
                        http_message = "语音播报指令发送成功"
                    elif '"Result" : false' in response_text or '"Result":false' in response_text or '"Result": false' in response_text or "'Result' : false" in response_text or "'Result':false" in response_text:
                        print(f"[语音测试调试] 检测到Result为false，语音播报失败")
                        http_success = False
                        http_message = "语音播报指令执行失败，返回结果为false"
                    else:
                        # 如果包含Result但值不明确，尝试提取
                        import re
                        result_match = re.search(r'"Result"\s*:\s*(true|false)', response_text, re.IGNORECASE)
                        if result_match:
                            result_value = result_match.group(1).lower()
                            if result_value == 'true':
                                http_success = True
                                http_message = "语音播报指令发送成功"
                            else:
                                http_success = False
                                http_message = f"语音播报指令执行失败，返回结果为{result_value}"
                        else:
                            http_success = False
                            http_message = f"无法从响应中提取Result值: {response_text[:200]}"
                else:
                    # 如果没有Result字段，直接检查是否包含true
                    if 'true' in response_text.lower():
                        print(f"[语音测试调试] 响应中包含true，判断为成功")
                        http_success = True
                        http_message = "语音播报指令发送成功"
                    else:
                        http_success = False
                        http_message = f"响应中未找到成功标识，返回数据: {response_text[:200]}"
            else:
                http_success = False
                http_message = f"HTTP请求失败，状态码: {response.status_code}, 响应: {response.text[:200]}"
                
        except requests.exceptions.Timeout:
            http_success = False
            http_message = "HTTP请求超时"
        except requests.exceptions.ConnectionError:
            http_success = False
            http_message = f"无法连接到设备 {ssh_host}:10086，请检查网络连接"
        except requests.exceptions.RequestException as e:
            http_success = False
            http_message = f"HTTP请求异常: {str(e)}"
        except Exception as e:
            http_success = False
            http_message = f"发送语音播报指令失败: {str(e)}"
        
        # 步骤4: 等待2秒
        print(f"[语音测试] 步骤4: HTTP请求完成，等待2秒...")
        time.sleep(2)
        print(f"[语音测试] 等待完成，开始执行roslaunch命令")
        
        # 步骤5: 执行 roslaunch task_manager task_manager.launch &
        try:
            print(f"[语音测试] 步骤5: 正在通过SSH执行命令: roslaunch task_manager task_manager.launch &")
            
            # 重新建立SSH连接（等待20秒后之前的连接可能已超时或关闭）
            try:
                if ssh and ssh.get_transport() and ssh.get_transport().is_active():
                    print(f"[语音测试] 使用现有SSH连接")
                else:
                    raise Exception("SSH连接不可用，需要重新建立")
            except:
                print(f"[语音测试] 重新建立SSH连接...")
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(
                    hostname=ssh_host,
                    port=22,
                    username=ssh_user,
                    password=ssh_password,
                    timeout=10,
                    allow_agent=False,
                    look_for_keys=False
                )
                print(f"[语音测试] SSH连接已重新建立")
            
            # 执行 roslaunch task_manager task_manager.launch & 命令（后台运行）
            # 需要先source ROS环境，因为exec_command不会自动加载环境变量
            # 使用bash -c确保shell正确执行
            command = "bash -c 'source /opt/ros/melodic/setup.bash 2>/dev/null || source /opt/ros/noetic/setup.bash 2>/dev/null || source ~/catkin_ws/devel/setup.bash 2>/dev/null || source $(find /opt/ros -name setup.bash 2>/dev/null | head -1) 2>/dev/null; roslaunch task_manager task_manager.launch &'"
            stdin, stdout, stderr = ssh.exec_command(command, timeout=10)
            
            # 对于后台命令，不等待退出状态，立即返回
            # 读取初始输出（如果有）
            time.sleep(0.5)  # 短暂等待，让命令开始执行
            if stdout.channel.recv_ready():
                output = stdout.read().decode('utf-8', errors='ignore')
                if output:
                    print(f"[语音测试] roslaunch命令输出: {output.strip()}")
            
            print(f"[语音测试] roslaunch命令已启动（后台运行）")
            
        except paramiko.AuthenticationException as e:
            print(f"[语音测试] ⚠️ SSH认证失败: {e}")
        except paramiko.SSHException as e:
            print(f"[语音测试] ⚠️ SSH连接错误: {e}")
        except Exception as e:
            print(f"[语音测试] ⚠️ roslaunch命令执行异常: {e}")
        finally:
            # 关闭SSH连接
            try:
                if ssh:
                    ssh.close()
                    print(f"[语音测试] SSH连接已关闭")
            except:
                pass
        
        # 步骤6: 等待10秒
        print(f"[语音测试] 步骤6: 等待10秒...")
        time.sleep(10)
        print(f"[语音测试] 等待完成，发送Ctrl+C操作")
        
        # 等待10秒后，发送Ctrl+C操作
        try:
            if ssh and ssh.get_transport() and ssh.get_transport().is_active():
                # 创建交互式shell通道来发送Ctrl+C
                channel = ssh.invoke_shell()
                channel.send(b'\x03')  # Ctrl+C (ASCII码3)
                time.sleep(0.5)  # 短暂等待
                channel.close()
                print(f"[语音测试] Ctrl+C操作已发送（步骤6后）")
        except Exception as e:
            print(f"[语音测试] ⚠️ 发送Ctrl+C操作失败（步骤6后）: {e}")
        
        print(f"[语音测试] 所有步骤执行完成")
        
        # 返回HTTP请求的结果（无论后续步骤是否成功，都以HTTP请求结果为准）
        if http_success:
            return {"status": "success", "message": http_message}
        else:
            return {"status": "error", "message": http_message}
    
    @staticmethod
    def check_io(item_id):
        """检查语音IO状态（如果需要）"""
        # 语音测试可能不需要IO检查，返回默认值
        return {"status": "success", "message": "语音测试无需IO检查"}
