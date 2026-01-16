# 相机/激光/TOF测试API处理器

from .base_api import BaseAPI
import config
import subprocess
import re
import time

class CameraAPI(BaseAPI):
    """相机/激光/TOF测试专用的API处理器"""
    
    @staticmethod
    def send_command(item_id, ssh_host=None, ssh_user=None, ssh_password=None):
        """发送相机测试指令（相机测试不需要发送命令，使用ping测试）"""
        # 相机测试不需要发送SSH命令，使用ping测试网络连通性
        return {"status": "success", "message": "该测试项使用ping测试，无需发送命令"}
    
    @staticmethod
    def ping_test(ip_address, timeout=10):
        """执行ping测试，检测网络连通性和丢包情况"""
        try:
            # 使用ping命令，持续timeout秒
            # Windows: ping -n {timeout} -w 1000 {ip}
            # Linux: ping -c {timeout} -W 1 {ip}
            import platform
            system = platform.system()
            
            if system == "Windows":
                # Windows系统：-n 指定发送次数，-w 指定超时时间（毫秒）
                # 每秒ping一次，持续timeout秒
                cmd = f"ping -n {timeout} -w 1000 {ip_address}"
            else:
                # Linux/Unix系统：-c 指定发送次数，-W 指定超时时间（秒）
                # 每秒ping一次，持续timeout秒
                cmd = f"ping -c {timeout} -W 1 {ip_address}"
            
            # 执行ping命令
            process = subprocess.Popen(
                cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # 等待命令完成（timeout + 2秒容错）
            stdout, stderr = process.communicate(timeout=timeout + 2)
            
            # 解析ping结果
            if system == "Windows":
                # Windows ping输出解析
                # 查找 "丢失 = X" 或 "Lost = X"
                lost_match = re.search(r'丢失\s*=\s*(\d+)', stdout) or re.search(r'Lost\s*=\s*(\d+)', stdout)
                # 查找 "已发送 = X" 或 "Packets: Sent = X"
                sent_match = re.search(r'已发送\s*=\s*(\d+)', stdout) or re.search(r'Packets:\s*Sent\s*=\s*(\d+)', stdout)
                
                if lost_match and sent_match:
                    lost = int(lost_match.group(1))
                    sent = int(sent_match.group(1))
                    received = sent - lost
                    packet_loss_rate = (lost / sent * 100) if sent > 0 else 100
                else:
                    # 如果无法解析，检查是否有"请求超时"或"Request timed out"
                    if "请求超时" in stdout or "Request timed out" in stdout or "无法访问" in stdout or "could not find host" in stdout.lower():
                        return {
                            "status": "success",
                            "test_status": "abnormal",
                            "packet_loss_rate": 100,
                            "message": "无法连接到设备"
                        }
                    else:
                        # 默认认为正常（有响应）
                        return {
                            "status": "success",
                            "test_status": "normal",
                            "packet_loss_rate": 0,
                            "message": "连接正常"
                        }
            else:
                # Linux ping输出解析
                # 查找 "X packets transmitted, Y received"
                stats_match = re.search(r'(\d+)\s+packets\s+transmitted,\s+(\d+)\s+received', stdout)
                if stats_match:
                    sent = int(stats_match.group(1))
                    received = int(stats_match.group(2))
                    lost = sent - received
                    packet_loss_rate = (lost / sent * 100) if sent > 0 else 100
                else:
                    # 如果无法解析，检查是否有错误
                    if "100% packet loss" in stdout or "Name or service not known" in stdout:
                        return {
                            "status": "success",
                            "test_status": "abnormal",
                            "packet_loss_rate": 100,
                            "message": "无法连接到设备"
                        }
                    else:
                        # 默认认为正常（有响应）
                        return {
                            "status": "success",
                            "test_status": "normal",
                            "packet_loss_rate": 0,
                            "message": "连接正常"
                        }
            
            # 判断结果：丢包率超过10%认为异常
            if packet_loss_rate > 10:
                test_status = "abnormal"
                message = f"丢包率过高: {packet_loss_rate:.1f}%"
            else:
                test_status = "normal"
                message = f"连接正常，丢包率: {packet_loss_rate:.1f}%"
            
            return {
                "status": "success",
                "test_status": test_status,
                "packet_loss_rate": packet_loss_rate,
                "sent": sent,
                "received": received,
                "lost": lost,
                "message": message
            }
            
        except subprocess.TimeoutExpired:
            process.kill()
            return {
                "status": "success",
                "test_status": "abnormal",
                "packet_loss_rate": 100,
                "message": "Ping测试超时"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Ping测试失败: {str(e)}"
            }
    
    @staticmethod
    def check_io(item_id, ssh_host=None, ssh_user=None, ssh_password=None, vehicle_model=None, test_id=None, ip_address=None, use_existing_ssh=False, ssh_connection=None):
        """检查相机IO状态（通过SSH在远程设备上执行ping测试）"""
        if not ip_address:
            return {"status": "error", "message": "未提供IP地址"}
        
        # 如果提供了SSH主机，通过SSH执行ping
        if ssh_host:
            return CameraAPI.ping_test_via_ssh(ip_address, ssh_host, ssh_user, ssh_password, timeout=config.PING_TEST_TIMEOUT, use_existing_ssh=use_existing_ssh, ssh_connection=ssh_connection)
        else:
            # 本地执行ping测试
            return CameraAPI.ping_test(ip_address, timeout=config.PING_TEST_TIMEOUT)
    
    @staticmethod
    def ping_test_via_ssh(ip_address, ssh_host, ssh_user=None, ssh_password=None, timeout=10, use_existing_ssh=False, ssh_connection=None):
        """通过SSH在远程设备上执行ping测试（使用交互式Shell实时读取输出）
        
        Args:
            ip_address: 要ping的目标IP
            ssh_host: SSH主机地址
            ssh_user: SSH用户名
            ssh_password: SSH密码
            timeout: ping测试持续时间（秒）
            use_existing_ssh: 是否使用已存在的SSH连接
            ssh_connection: 可选的SSH连接对象（如果提供，直接使用）
        """
        import paramiko
        
        ssh_user = ssh_user or config.SSH_USER
        ssh_password = ssh_password or config.SSH_PASSWORD
        
        ssh = None
        channel = None
        should_close_ssh = False  # 标记是否需要关闭SSH连接
        
        try:
            # 1. 获取SSH连接（使用已存在的或新建）
            if ssh_connection:
                # 如果直接提供了SSH连接对象，使用它
                ssh = ssh_connection
                print(f"[相机测试] ✅ 使用提供的SSH连接: {ssh_host}，开始对 {ip_address} 执行ping测试（持续{timeout}秒）...")
            elif use_existing_ssh:
                # 尝试从连接池获取（通过全局变量访问）
                try:
                    # 延迟导入app模块，避免循环导入
                    import sys
                    app_module = sys.modules.get('app')
                    if app_module and hasattr(app_module, 'camera_ssh_connections'):
                        camera_ssh_connections = app_module.camera_ssh_connections
                        if ssh_host in camera_ssh_connections:
                            ssh_info = camera_ssh_connections[ssh_host]
                            ssh = ssh_info['ssh']
                            print(f"[相机测试] ✅ 使用已存在的SSH连接: {ssh_host}，开始对 {ip_address} 执行ping测试（持续{timeout}秒）...")
                        else:
                            print(f"[相机测试] ⚠️ 未找到已存在的SSH连接: {ssh_host}，将新建连接")
                            use_existing_ssh = False
                    else:
                        print(f"[相机测试] ⚠️ 连接池不可用，将新建连接")
                        use_existing_ssh = False
                except Exception as e:
                    print(f"[相机测试] ⚠️ 获取已存在SSH连接失败: {str(e)}，将新建连接")
                    use_existing_ssh = False
            
            # 如果还没有SSH连接，建立新的连接
            if ssh is None:
                # 建立新的SSH连接
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(
                    hostname=ssh_host,
                    username=ssh_user,
                    password=ssh_password,
                    timeout=config.SSH_TIMEOUT,
                    look_for_keys=False,
                    allow_agent=False
                )
                should_close_ssh = True  # 标记需要关闭
                print(f"[相机测试] ✅ 成功SSH连接到 {ssh_host}，开始对 {ip_address} 执行ping测试（持续{timeout}秒）...")
            
            # 2. 创建交互式Shell通道（支持持续输出）
            channel = ssh.invoke_shell()
            channel.settimeout(timeout + 5)  # 超时时间留余量
            channel.set_combine_stderr(True)
            
            # 3. 发送ping命令（Linux系统，持续ping直到手动停止）
            # -i 1 每秒ping一次，不指定-c（持续ping），后续通过时间控制停止
            ping_cmd = f"ping {ip_address} -i 1\n"
            channel.send(ping_cmd)
            time.sleep(1)  # 等待ping命令启动
            
            # 4. 实时读取ping输出并解析
            start_time = time.time()
            ping_stats = {
                "packet_sent": 0,      # 发送包数
                "packet_received": 0,  # 接收包数
                "packet_loss": 0.0,    # 丢包率
                "avg_delay": 0.0       # 平均延迟(ms)
            }
            all_output = ""  # 存储所有输出用于调试
            
            print(f"[相机测试] 📤 ping {ip_address} 实时输出：")
            print("-" * 80)
            
            while time.time() - start_time < timeout:
                if channel.recv_ready():
                    output = channel.recv(4096).decode('utf-8', errors='ignore')
                    if output:
                        all_output += output
                        print(output.strip())  # 打印原始ping输出
                        
                        # 解析单条ping结果（匹配"time=xx.xx ms"或"time=xx ms"）
                        delay_match = re.search(r'time=(\d+\.?\d*)\s*ms', output)
                        if delay_match:
                            ping_stats["packet_sent"] += 1
                            ping_stats["packet_received"] += 1
                            delay = float(delay_match.group(1))
                            # 计算平均延迟
                            if ping_stats["packet_received"] == 1:
                                ping_stats["avg_delay"] = delay
                            else:
                                ping_stats["avg_delay"] = (ping_stats["avg_delay"] * (ping_stats["packet_received"] - 1) + delay) / ping_stats["packet_received"]
                        
                        # 解析丢包（匹配"Request timeout"或超时信息）
                        if "Request timeout" in output or "100% packet loss" in output or "no answer" in output.lower():
                            ping_stats["packet_sent"] += 1
                
                time.sleep(0.1)  # 每隔0.1秒读取一次
            
            # 5. 停止ping命令（发送Ctrl+C）
            channel.send("\x03")  # 发送中断信号
            time.sleep(1)
            
            # 6. 计算丢包率并输出汇总
            print("-" * 80)
            print(f"\n[相机测试] 📊 ping测试汇总结果：")
            
            if ping_stats["packet_sent"] > 0:
                ping_stats["packet_loss"] = ((ping_stats["packet_sent"] - ping_stats["packet_received"]) / ping_stats["packet_sent"]) * 100
                print(f"   目标IP: {ip_address}")
                print(f"   测试时长: {timeout}秒")
                print(f"   发送包数: {ping_stats['packet_sent']}")
                print(f"   接收包数: {ping_stats['packet_received']}")
                print(f"   丢包率: {ping_stats['packet_loss']:.1f}%")
                print(f"   平均延迟: {ping_stats['avg_delay']:.2f} ms")
                
                # 判断结果：0%丢包才正常，否则异常
                if ping_stats["packet_loss"] == 0:
                    test_status = "normal"
                    message = f"连接正常，丢包率: {ping_stats['packet_loss']:.1f}%，平均延迟: {ping_stats['avg_delay']:.2f} ms"
                    print(f"[相机测试] ✅ 0%丢包，标记为正常")
                else:
                    test_status = "abnormal"
                    message = f"有丢包，丢包率: {ping_stats['packet_loss']:.1f}%，平均延迟: {ping_stats['avg_delay']:.2f} ms"
                    print(f"[相机测试] ❌ 丢包率={ping_stats['packet_loss']:.1f}%，标记为异常")
                
                return {
                    "status": "success",
                    "test_status": test_status,
                    "packet_loss_rate": ping_stats["packet_loss"],
                    "sent": ping_stats["packet_sent"],
                    "received": ping_stats["packet_received"],
                    "lost": ping_stats["packet_sent"] - ping_stats["packet_received"],
                    "avg_delay": ping_stats["avg_delay"],
                    "message": message
                }
            else:
                # 未获取到有效ping数据
                print(f"   ⚠️  未获取到有效ping数据，可能目标IP不可达或网络异常")
                print(f"   完整输出: {all_output[:500]}")
                return {
                    "status": "success",
                    "test_status": "abnormal",
                    "packet_loss_rate": 100,
                    "sent": 0,
                    "received": 0,
                    "lost": 0,
                    "avg_delay": 0,
                    "message": "未获取到有效ping数据，可能目标IP不可达或网络异常"
                }
            
        except paramiko.AuthenticationException:
            return {"status": "error", "message": "SSH认证失败"}
        except paramiko.SSHException as e:
            return {"status": "error", "message": f"SSH连接错误: {str(e)}"}
        except Exception as e:
            # 对于超时或其他异常，也应该标记为异常
            error_msg = str(e)
            if "timeout" in error_msg.lower() or "timed out" in error_msg.lower():
                return {
                    "status": "success",
                    "test_status": "abnormal",
                    "packet_loss_rate": 100,
                    "sent": 0,
                    "received": 0,
                    "lost": 0,
                    "avg_delay": 0,
                    "message": "Ping测试超时"
                }
            return {"status": "error", "message": f"Ping测试失败: {error_msg}"}
        finally:
            # 关闭通道（每次ping都需要关闭通道）
            if channel:
                try:
                    channel.close()
                except:
                    pass
            
            # 只有在新建连接时才关闭SSH（使用已存在连接时不关闭）
            if should_close_ssh and ssh:
                try:
                    ssh.close()
                    print(f"[相机测试] 🔌 SSH连接已关闭")
                except:
                    pass
            elif use_existing_ssh:
                print(f"[相机测试] ✅ 保持SSH连接打开（供后续使用）")
    
    @staticmethod
    def check_tof_subscribe(item_id, ssh_host=None, ssh_user=None, ssh_password=None, vehicle_model=None, test_id=None, use_existing_ssh=False, ssh_connection=None):
        """检查TOF订阅状态（通过SSH执行rostopic命令，订阅TOF话题）
        
        Args:
            item_id: 测试项ID（'front_tof' 或 'rear_tof'）
            ssh_host: SSH主机地址
            ssh_user: SSH用户名
            ssh_password: SSH密码
            vehicle_model: 车型（未使用，保留兼容性）
            test_id: 测试ID（未使用，保留兼容性）
            use_existing_ssh: 是否使用已存在的SSH连接
            ssh_connection: 可选的SSH连接对象（如果提供，直接使用）
        """
        import paramiko
        import time
        
        # 根据item_id确定订阅话题
        if item_id == 'front_tof':
            topic = config.TOF_FRONT_TOPIC
            tof_name = '前TOF'
        elif item_id == 'rear_tof':
            topic = config.TOF_REAR_TOPIC
            tof_name = '后TOF'
        else:
            return {"status": "error", "message": f"未知的TOF测试项: {item_id}"}
        
        print(f"[TOF测试] 开始订阅 {tof_name} 话题: {topic}")
        
        if not ssh_host:
            return {"status": "error", "message": "未提供SSH主机地址"}
        
        ssh_user = ssh_user or config.SSH_USER
        ssh_password = ssh_password or config.SSH_PASSWORD
        
        ssh = None
        channel = None
        should_close_ssh = False
        
        try:
            # 1. 获取SSH连接（使用已存在的或新建）
            if ssh_connection:
                ssh = ssh_connection
                print(f"[TOF测试] ✅ 使用提供的SSH连接: {ssh_host}，开始订阅 {tof_name} 话题...")
            elif use_existing_ssh:
                try:
                    import sys
                    app_module = sys.modules.get('app')
                    if app_module and hasattr(app_module, 'camera_ssh_connections'):
                        camera_ssh_connections = app_module.camera_ssh_connections
                        if ssh_host in camera_ssh_connections:
                            ssh_info = camera_ssh_connections[ssh_host]
                            ssh = ssh_info['ssh']
                            print(f"[TOF测试] ✅ 使用已存在的SSH连接: {ssh_host}，开始订阅 {tof_name} 话题...")
                        else:
                            print(f"[TOF测试] ⚠️ 未找到已存在的SSH连接: {ssh_host}，将新建连接")
                            use_existing_ssh = False
                    else:
                        print(f"[TOF测试] ⚠️ 连接池不可用，将新建连接")
                        use_existing_ssh = False
                except Exception as e:
                    print(f"[TOF测试] ⚠️ 获取已存在SSH连接失败: {str(e)}，将新建连接")
                    use_existing_ssh = False
            
            # 如果还没有SSH连接，建立新的连接
            if ssh is None:
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(
                    hostname=ssh_host,
                    username=ssh_user,
                    password=ssh_password,
                    timeout=config.SSH_TIMEOUT,
                    look_for_keys=False,
                    allow_agent=False
                )
                should_close_ssh = True
                print(f"[TOF测试] ✅ 成功SSH连接到 {ssh_host}，开始订阅 {tof_name} 话题...")
            
            # 2. 创建交互式Shell通道
            channel = ssh.invoke_shell()
            timeout = config.TOF_SUBSCRIBE_TIMEOUT  # 使用配置的超时时间（30秒）
            channel.settimeout(timeout + 5)  # 通道超时时间留余量
            channel.set_combine_stderr(True)
            
            # 3. 发送rostopic echo指令（订阅话题）
            rostopic_cmd = f"rostopic echo {topic}\n"
            channel.send(rostopic_cmd)
            time.sleep(1)  # 等待指令执行和话题数据返回
            
            # 4. 实时读取输出，每5秒检查一次是否有数据
            start_time = time.time()
            has_data = False  # 标记是否收到数据
            all_output = ""  # 存储所有原始输出用于调试
            last_check_time = start_time  # 上次检查的时间
            check_interval = 5  # 每5秒检查一次
            
            print(f"[TOF测试] 开始接收 {tof_name} 话题数据（超时时间{timeout}秒，每{check_interval}秒检查一次）：")
            print("-" * 60)
            
            # 持续读取数据，每5秒检查一次是否有数据
            while time.time() - start_time < timeout:
                if channel.recv_ready():
                    output = channel.recv(4096).decode('utf-8', errors='ignore')
                    if output:
                        all_output += output
                        # 打印所有原始输出（完整数据）
                        print(f"[TOF测试] [{tof_name}] 原始输出:\n{output}")
                        print("-" * 60)
                
                # 每5秒检查一次是否有有效数据
                current_time = time.time()
                if current_time - last_check_time >= check_interval:
                    last_check_time = current_time
                    
                    # 检查是否有有效数据（排除提示符、命令回显等）
                    if all_output:
                        # 查找有效数据（排除提示符、命令回显、空行等）
                        lines = all_output.split('\n')
                        for line in lines:
                            line_clean = line.strip()
                            # 如果输出包含非空内容（排除提示符、命令回显、空行等）
                            if line_clean and not line_clean.startswith('[') and 'echo' not in line_clean.lower():
                                # 检查是否包含实际数据（不是提示符或命令回显）
                                if len(line_clean) > 10:  # 至少10个字符，可能是有效数据
                                    has_data = True
                                    print(f"[TOF测试] [{tof_name}] 检测到有效数据（长度: {len(line_clean)} 字符），立即返回结果")
                                    # 检测到数据，立即停止订阅并返回
                                    try:
                                        channel.send(b'\x03')  # Ctrl+C
                                        time.sleep(0.1)
                                        print(f"[TOF测试] 已发送Ctrl+C停止 {tof_name} 话题订阅")
                                    except:
                                        pass
                                    break
                    
                    # 如果检测到数据，跳出循环
                    if has_data:
                        break
                
                time.sleep(0.5)  # 每隔0.5秒读取一次
            
            # 5. 如果还没有停止，停止rostopic订阅（发送Ctrl+C）
            if not has_data:
                try:
                    channel.send(b'\x03')  # Ctrl+C
                    time.sleep(0.1)
                    print(f"[TOF测试] 已发送Ctrl+C停止 {tof_name} 话题订阅")
                except:
                    pass
            
            # 6. 判断结果
            print("-" * 60)
            print(f"\n[TOF测试] 📊 {tof_name} 订阅结果汇总：")
            print(f"   话题: {topic}")
            print(f"   测试时长: {timeout}秒")
            print(f"   是否收到数据: {'是' if has_data else '否'}")
            print(f"   完整输出长度: {len(all_output)} 字符")
            print(f"\n[TOF测试] 📄 {tof_name} 完整输出内容：")
            print("=" * 80)
            print(all_output)
            print("=" * 80)
            
            if has_data:
                print(f"\n[TOF测试] ✅ {tof_name} 订阅成功，收到数据，标记为正常")
                return {
                    "status": "success",
                    "test_status": "normal",
                    "message": f"{tof_name} 订阅成功，已收到数据",
                    "raw_output": all_output  # 返回原始输出供前端查看
                }
            else:
                print(f"\n[TOF测试] ❌ {tof_name} 订阅超时，未收到数据，标记为异常")
                return {
                    "status": "success",
                    "test_status": "abnormal",
                    "message": f"{tof_name} 订阅超时，未收到数据",
                    "raw_output": all_output  # 返回原始输出供前端查看
                }
                
        except paramiko.AuthenticationException:
            return {"status": "error", "message": "SSH认证失败"}
        except paramiko.SSHException as e:
            return {"status": "error", "message": f"SSH连接错误: {str(e)}"}
        except TimeoutError:
            print(f"[TOF测试] ⏰ {tof_name} 订阅超时（{timeout}秒），已停止")
            return {"status": "success", "test_status": "abnormal", "message": f"{tof_name} 订阅超时（{timeout}秒），未收到数据"}
        except Exception as e:
            return {"status": "error", "message": f"TOF订阅检查错误: {str(e)}"}
        finally:
            # 关闭通道和SSH连接（确保一定会关闭）
            if channel:
                try:
                    channel.close()
                except:
                    pass
            
            # 只有在新建连接时才关闭SSH（使用已存在连接时不关闭）
            if should_close_ssh and ssh:
                try:
                    ssh.close()
                    print(f"[TOF测试] 🔌 SSH连接已关闭")
                except:
                    pass
            elif use_existing_ssh:
                print(f"[TOF测试] ✅ 保持SSH连接打开（供后续使用）")
