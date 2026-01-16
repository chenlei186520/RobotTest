# 基础API处理器
# 所有测试类别的API处理器都应该继承此类

class BaseAPI:
    """基础API处理器，提供默认的API处理方法"""
    
    @staticmethod
    def send_command(item_id, command_map=None, ssh_host=None, ssh_user=None, ssh_password=None):
        """发送指令的默认实现（通过SSH）"""
        import config
        
        # 如果没有提供command_map或item_id不在command_map中，表示该测试项不需要发送命令
        # 用户可以直接选择结果
        if not command_map or item_id not in command_map:
            return {"status": "success", "message": "该测试项无需发送命令，请直接选择结果"}
        
        command = command_map[item_id]
        
        # 如果提供了SSH主机，通过SSH执行
        if ssh_host:
            ssh_user = ssh_user or config.SSH_USER
            ssh_password = ssh_password or config.SSH_PASSWORD
            
            # 打印调试信息（可在生产环境中移除）
            print(f"[SSH调试] 尝试连接: {ssh_user}@{ssh_host}")
            print(f"[SSH调试] 执行命令: {command}")
            
            try:
                import paramiko
                
                # 创建SSH客户端
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                
                # 连接SSH服务器
                try:
                    ssh.connect(
                        hostname=ssh_host,
                        username=ssh_user,
                        password=ssh_password,
                        timeout=config.SSH_TIMEOUT,
                        look_for_keys=False,
                        allow_agent=False
                    )
                    print(f"[SSH调试] 连接成功")
                except Exception as conn_error:
                    print(f"[SSH调试] 连接失败: {str(conn_error)}")
                    raise
                
                # 执行命令
                try:
                    stdin, stdout, stderr = ssh.exec_command(command, timeout=config.SSH_TIMEOUT)
                    
                    # 等待命令执行完成
                    exit_status = stdout.channel.recv_exit_status()
                    
                    # 读取输出（用于调试）
                    stdout_text = stdout.read().decode('utf-8', errors='ignore').strip()
                    stderr_text = stderr.read().decode('utf-8', errors='ignore').strip()
                    
                    print(f"[SSH调试] 命令退出状态: {exit_status}")
                    if stdout_text:
                        print(f"[SSH调试] 标准输出: {stdout_text}")
                    if stderr_text:
                        print(f"[SSH调试] 错误输出: {stderr_text}")
                    
                    if exit_status == 0:
                        # 不立即关闭连接，返回SSH对象信息用于后续关闭
                        # 注意：这里不能直接返回SSH对象（无法序列化），需要在后台线程中保持连接
                        import threading
                        import time
                        
                        # 在后台线程中保持连接指定时间后关闭
                        def close_connection_after_delay(ssh_conn, delay_seconds):
                            time.sleep(delay_seconds)
                            try:
                                ssh_conn.close()
                                print(f"[SSH调试] 连接已自动关闭（保持{delay_seconds}秒后）")
                            except:
                                pass
                        
                        hold_time = getattr(config, 'SSH_CONNECTION_HOLD_TIME', 30)
                        thread = threading.Thread(
                            target=close_connection_after_delay,
                            args=(ssh, hold_time),
                            daemon=True
                        )
                        thread.start()
                        print(f"[SSH调试] 连接将保持{hold_time}秒后自动关闭")
                        
                        return {"status": "success", "message": "指令发送成功"}
                    else:
                        error_msg = stderr_text if stderr_text else "命令执行失败"
                        ssh.close()
                        return {"status": "error", "message": f"指令执行失败: {error_msg}"}
                except Exception as exec_error:
                    ssh.close()
                    print(f"[SSH调试] 命令执行异常: {str(exec_error)}")
                    raise
                    
            except paramiko.AuthenticationException as e:
                error_msg = f"SSH认证失败：用户名({ssh_user})或密码错误，请检查config.py中的SSH_USER和SSH_PASSWORD配置"
                print(f"[SSH调试] {error_msg}")
                return {"status": "error", "message": error_msg}
            except paramiko.SSHException as e:
                error_msg = f"SSH连接错误: {str(e)}。请检查：1) SSH服务器是否运行 2) IP地址是否正确 3) 网络是否可达"
                print(f"[SSH调试] {error_msg}")
                return {"status": "error", "message": error_msg}
            except paramiko.socket.timeout:
                error_msg = f"SSH连接超时（{config.SSH_TIMEOUT}秒）。请检查：1) IP地址是否正确 2) 网络是否可达 3) 防火墙设置"
                print(f"[SSH调试] {error_msg}")
                return {"status": "error", "message": error_msg}
            except Exception as e:
                error_msg = f"执行错误: {str(e)}。错误类型: {type(e).__name__}"
                print(f"[SSH调试] {error_msg}")
                return {"status": "error", "message": error_msg}
        else:
            # 本地执行（用于测试）
            import subprocess
            try:
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if result.returncode == 0:
                    return {"status": "success", "message": "指令发送成功"}
                else:
                    error_msg = result.stderr.strip() if result.stderr else result.stdout.strip()
                    return {"status": "error", "message": f"指令执行失败: {error_msg}"}
            except Exception as e:
                return {"status": "error", "message": f"执行错误: {str(e)}"}
    
    @staticmethod
    def check_io(item_id, io_index_map, ros_topic, ros_timeout, io_timeout, ssh_host=None, ssh_user=None, ssh_password=None):
        """检查IO状态的默认实现（支持SSH远程执行）"""
        import config
        import re
        
        if item_id not in io_index_map:
            return {"status": "error", "message": "未知的测试项"}
        
        io_index = io_index_map[item_id]
        
        # 如果提供了SSH主机，通过SSH执行
        if ssh_host:
            ssh_user = ssh_user or config.SSH_USER
            ssh_password = ssh_password or config.SSH_PASSWORD
            
            try:
                import paramiko
                
                # 创建SSH客户端
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                
                # 连接SSH服务器
                ssh.connect(
                    hostname=ssh_host,
                    username=ssh_user,
                    password=ssh_password,
                    timeout=config.SSH_TIMEOUT,
                    look_for_keys=False,
                    allow_agent=False
                )
                
                # 执行rostopic命令
                command = f"timeout {ros_timeout} rostopic echo -n 1 {ros_topic}"
                stdin, stdout, stderr = ssh.exec_command(command, timeout=ros_timeout + 5)
                exit_status = stdout.channel.recv_exit_status()
                
                if exit_status == 0:
                    output = stdout.read().decode('utf-8', errors='ignore')
                    int_data = None
                    
                    # 解析输出，只关心第二个int_data（第一个---分隔符后的）
                    lines = output.split('\n')
                    found_first_separator = False
                    
                    for line in lines:
                        # 检测到第一个---分隔符
                        if line.strip() == '---':
                            found_first_separator = True
                            continue
                        
                        # 在第一个---分隔符后查找int_data
                        if found_first_separator and 'int_data:' in line:
                            match = re.search(r'\[(.*?)\]', line)
                            if match:
                                data_str = match.group(1)
                                int_data = [int(x.strip()) for x in data_str.split(',') if x.strip()]
                                break
                    
                    ssh.close()
                    
                    if int_data and len(int_data) > io_index:
                        io_value = int_data[io_index]
                        status = "normal" if io_value == 0 else "abnormal"
                        return {
                            "status": "success",
                            "io_value": io_value,
                            "test_status": status
                        }
                    else:
                        return {"status": "error", "message": "无法解析IO数据"}
                else:
                    error_msg = stderr.read().decode('utf-8', errors='ignore').strip()
                    ssh.close()
                    return {"status": "error", "message": f"获取IO数据失败: {error_msg}"}
                    
            except paramiko.AuthenticationException:
                return {"status": "error", "message": "SSH认证失败"}
            except paramiko.SSHException as e:
                return {"status": "error", "message": f"SSH连接错误: {str(e)}"}
            except Exception as e:
                return {"status": "error", "message": f"检查错误: {str(e)}"}
        else:
            # 本地执行（用于测试）
            import subprocess
            try:
                command = f"timeout {ros_timeout} rostopic echo -n 1 {ros_topic}"
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=ros_timeout + 5
                )
                
                if result.returncode == 0:
                    output = result.stdout
                    int_data = None
                    
                    # 解析输出，只关心第二个int_data（第一个---分隔符后的）
                    lines = output.split('\n')
                    found_first_separator = False
                    
                    for line in lines:
                        # 检测到第一个---分隔符
                        if line.strip() == '---':
                            found_first_separator = True
                            continue
                        
                        # 在第一个---分隔符后查找int_data
                        if found_first_separator and 'int_data:' in line:
                            match = re.search(r'\[(.*?)\]', line)
                            if match:
                                data_str = match.group(1)
                                int_data = [int(x.strip()) for x in data_str.split(',') if x.strip()]
                                break
                    
                    if int_data and len(int_data) > io_index:
                        io_value = int_data[io_index]
                        status = "normal" if io_value == 0 else "abnormal"
                        return {
                            "status": "success",
                            "io_value": io_value,
                            "test_status": status
                        }
                    else:
                        return {"status": "error", "message": "无法解析IO数据"}
                else:
                    return {"status": "error", "message": f"获取IO数据失败: {result.stderr}"}
            except subprocess.TimeoutExpired:
                return {"status": "error", "message": f"超时：{io_timeout}秒内未收到IO信号"}
            except Exception as e:
                return {"status": "error", "message": f"检查错误: {str(e)}"}
