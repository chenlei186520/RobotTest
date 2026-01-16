# 按键测试API处理器

from .base_api import BaseAPI
import config

class ButtonAPI(BaseAPI):
    """按键测试专用的API处理器"""
    
    @staticmethod
    def send_command(item_id, ssh_host=None, ssh_user=None, ssh_password=None):
        """发送按键测试指令（按键测试无需发送命令，等待用户点击按钮）"""
        # 按键测试不需要在send_command阶段发送订阅指令
        # 订阅指令会在check_io阶段发送，避免重复订阅
        if not ssh_host:
            return {"status": "success", "message": "该测试项无需发送命令，请手动点击设备上的按钮"}
        
        # 直接返回成功，不发送任何SSH指令
        # 实际的rostopic订阅会在check_io方法中发送
        print(f"[按键测试] 跳过send_command阶段的订阅，将在check_io阶段发送订阅指令")
        return {"status": "success", "message": "已准备就绪，请点击设备上的按钮"}
    
    @staticmethod
    def check_io(item_id, ssh_host=None, ssh_user=None, ssh_password=None, vehicle_model=None, test_id=None):
        """检查IO状态（通过SSH执行rostopic命令，从CSV动态匹配按钮）"""
        import paramiko
        import re
        import time
        
        vehicle = vehicle_model
        print(f"[按键测试调试] 开始检查IO，item_id={item_id}, vehicle={vehicle}")
        
        # 获取按钮名称（从button_test.py或touch_test.py中查找）
        button_name = None
        try:
            # 先尝试从按键测试数据中查找
            from test_data import button_test
            for section in button_test.BUTTON_TEST_DATA.get('sections', []):
                for item in section.get('items', []):
                    if item.get('id') == item_id:
                        button_name = item.get('name')
                        print(f"[按键测试调试] 从按键测试数据中找到按钮名称: {button_name}")
                        break
                if button_name:
                    break
            
            # 如果没找到，尝试从触边测试数据中查找
            if not button_name:
                from test_data import touch_test
                for section in touch_test.TOUCH_TEST_DATA.get('sections', []):
                    for item in section.get('items', []):
                        if item.get('id') == item_id:
                            button_name = item.get('name')
                            print(f"[按键测试调试] 从触边测试数据中找到按钮名称: {button_name}")
                            break
                    if button_name:
                        break
        except Exception as e:
            print(f"[按键测试] 获取按钮名称失败: {e}")
        
        if not button_name:
            print(f"[按键测试调试] 未找到按钮名称，回退到使用配置的IO映射")
            # 如果无法获取按钮名称，回退到使用配置的IO映射
            io_index_map = config.get_button_io_map(vehicle)
            return BaseAPI.check_io(
                item_id,
                io_index_map,
                config.ROS_TOPIC,
                config.ROS_COMMAND_TIMEOUT,
                config.IO_CHECK_TIMEOUT,
                ssh_host,
                ssh_user,
                ssh_password
            )
        
        # 从CSV中查找按钮对应的IO索引和值的含义
        print(f"[按键测试调试] 从CSV查找按钮映射，button_name={button_name}, vehicle={vehicle}")
        mapping = config.parse_button_mapping_from_csv(vehicle, button_name)
        
        if not mapping:
            print(f"[按键测试] 未找到按钮 '{button_name}' 在车型 '{vehicle}' 中的映射，回退到使用配置的IO映射")
            # 回退到使用配置的IO映射
            io_index_map = config.get_button_io_map(vehicle)
            return BaseAPI.check_io(
                item_id,
                io_index_map,
                config.ROS_TOPIC,
                config.ROS_COMMAND_TIMEOUT,
                config.IO_CHECK_TIMEOUT,
                ssh_host,
                ssh_user,
                ssh_password
            )
        
        print(f"[按键测试调试] CSV映射成功: {mapping}")
        
        io_index = mapping['io_index']
        value_meaning = mapping['value_meaning']
        
        # 解析值的含义
        # 注意：根据实际硬件逻辑，按下按钮后IO=0，弹起时IO=1
        # 所以无论CSV中怎么写，按下按钮后int_data[io_index]应该是0
        print(f"[按键测试调试] 值的含义: '{value_meaning}'")
        
        # 根据实际硬件逻辑：按下按钮后，IO值应该是0
        # 所以expected_value应该是0（按下状态）
        expected_value = 0  # 按下按钮后，IO值应该是0
        
        print(f"[按键测试调试] expected_value={expected_value} (按下按钮后IO值应该是0)")
        
        if not ssh_host:
            return {"status": "error", "message": "未提供SSH主机地址"}
        
        ssh_user = ssh_user or config.SSH_USER
        ssh_password = ssh_password or config.SSH_PASSWORD
        
        channel = None
        try:
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
            print("✅ SSH连接成功，开始订阅ROS话题 {}...".format(config.ROS_TOPIC))
            
            # 创建交互式Shell通道（关键：支持持续输出的指令）
            channel = ssh.invoke_shell()
            timeout = config.IO_CHECK_TIMEOUT  # 使用配置的超时时间（30秒）
            channel.settimeout(timeout)  # 通道超时时间
            channel.set_combine_stderr(True)  # 合并标准输出和错误输出
            
            # 发送rostopic echo指令（订阅话题）
            rostopic_cmd = f"rostopic echo {config.ROS_TOPIC}\n"
            channel.send(rostopic_cmd)
            time.sleep(1)  # 等待指令执行和话题数据返回
            
            # 实时读取输出并解析IO状态
            start_time = time.time()
            int_data = None  # 存储解析后的int_data数组（保留最后一次有效解析）
            all_output = ""  # 存储所有原始输出
            last_check_time = start_time  # 上次检查匹配的时间
            check_interval = 5  # 每隔5秒检查一次匹配
            match_success = False  # 标记是否匹配成功
            
            print("📤 开始接收话题数据（超时时间{}秒，每{}秒检查一次匹配）：".format(timeout, check_interval))
            print("-" * 60)
            
            # 持续读取数据，每隔5秒检查一次匹配
            while time.time() - start_time < timeout:
                if channel.recv_ready():
                    # 读取通道数据（按字节读取，避免截断）
                    output = channel.recv(4096).decode('utf-8', errors='ignore')
                    if output:
                        all_output += output
                        print(output.strip())  # 打印原始输出
                        
                        # 解析int_data数组（正则匹配，支持多行）
                        # 注意：rostopic输出可能跨多行，需要在整个all_output中搜索最新的int_data
                        # 使用findall获取所有匹配，取最后一个（最新的）
                        int_data_matches = re.findall(r'int_data:\s*\[([0-9, \n]*)\]', all_output, re.MULTILINE | re.DOTALL)
                        if int_data_matches:
                            # 从后往前查找，找到最后一个非空的int_data
                            parsed_int_data = None
                            for int_data_str in reversed(int_data_matches):
                                # 移除换行符，保留空格（用于分割）
                                int_data_str_clean = int_data_str.replace('\n', ' ').strip()
                                if int_data_str_clean:  # 非空数组
                                    parsed_int_data = [int(x.strip()) for x in int_data_str_clean.split(',') if x.strip()]
                                    if parsed_int_data:  # 确保数组不为空
                                        break  # 找到有效的int_data，退出循环
                            
                            # 只有找到非空的int_data才更新
                            if parsed_int_data:
                                # 保存最后一次有效的int_data（不覆盖已有的有效数据，除非新数据也是有效的）
                                int_data = parsed_int_data
                                print(f"🔍 解析到IO触发数据: {int_data}")
                                
                                # 每隔5秒检查一次匹配
                                current_time = time.time()
                                if current_time - last_check_time >= check_interval:
                                    last_check_time = current_time
                                    
                                    # 检查匹配
                                    if len(int_data) > io_index:
                                        actual_value = int_data[io_index]
                                        expected_value = 0
                                        
                                        print(f"[按键测试] 检查匹配: 预期结果({expected_value}) vs 实际结果({actual_value})")
                                        
                                        if actual_value == expected_value:
                                            # 匹配成功，立即停止订阅
                                            match_success = True
                                            print("✅ 匹配成功，立即停止SSH订阅...")
                                            try:
                                                channel.send(b'\x03')  # Ctrl+C
                                                time.sleep(0.1)
                                                print("🛑 已发送Ctrl+C停止rostopic订阅")
                                            except:
                                                pass
                                            break  # 跳出循环
                                        else:
                                            print(f"❌ 匹配失败: 预期结果({expected_value}) != 实际结果({actual_value})，继续等待...")
                            # 空数组不打印，避免干扰
                
                time.sleep(0.5)  # 每隔0.5秒读取一次
            
            # 如果匹配成功，立即关闭通道
            if match_success and channel:
                try:
                    channel.send(b'\x03')  # Ctrl+C
                    time.sleep(0.1)
                except:
                    pass
            
            # 输出最终解析结果
            print("-" * 60)
            
            # 调试：打印int_data状态
            if int_data:
                print(f"[调试] 循环结束后的int_data: {int_data}, 长度: {len(int_data)}")
            else:
                print(f"[调试] 循环结束后int_data为None或空，尝试从all_output解析...")
                # 如果int_data为None，尝试从all_output中解析（支持多行，取最后一个匹配）
                int_data_matches = re.findall(r'int_data:\s*\[([0-9, \n]*)\]', all_output, re.MULTILINE | re.DOTALL)
                if int_data_matches:
                    # 取最后一个匹配（最新的int_data）
                    int_data_str = int_data_matches[-1]
                    # 移除换行符，保留空格（用于分割）
                    int_data_str = int_data_str.replace('\n', ' ').strip()
                    if int_data_str:
                        int_data = [int(x.strip()) for x in int_data_str.split(',') if x.strip()]
                        print(f"[调试] 从all_output解析到int_data: {int_data}")
            
            # 如果匹配成功，立即返回结果
            if match_success and int_data and len(int_data) > io_index:
                actual_value = int_data[io_index]
                expected_value = 0
                
                print(f"[按键测试] 按钮 '{button_name}' 对应 IO索引: {io_index}")
                print(f"[按键测试] 预期结果: {expected_value}")
                print(f"[按键测试] 实际结果: {actual_value}")
                print(f"[按键测试] ✅ 匹配成功: 预期结果({expected_value}) == 实际结果({actual_value})，自动勾选【正常】")
                
                result = {
                    "status": "success",
                    "io_value": actual_value,
                    "test_status": "normal",
                    "io_index": io_index,
                    "button_name": button_name,
                    "int_data": int_data,
                    "expected_value": expected_value
                }
                return result
            
            # 如果匹配失败或超时，检查最终数据是否匹配
            if int_data:
                # 有数据，检查是否匹配
                if len(int_data) > io_index:
                    actual_value = int_data[io_index]
                    expected_value = 0
                    print(f"[按键测试] 按钮 '{button_name}' 对应 IO索引: {io_index}")
                    print(f"[按键测试] 预期结果: {expected_value}")
                    print(f"[按键测试] 实际结果: {actual_value}")
                    
                    # 最终检查：如果实际值和预期值相等，应该返回成功
                    if actual_value == expected_value:
                        print(f"[按键测试] ✅ 最终匹配成功: 预期结果({expected_value}) == 实际结果({actual_value})，自动勾选【正常】")
                        result = {
                            "status": "success",
                            "io_value": actual_value,
                            "test_status": "normal",
                            "io_index": io_index,
                            "button_name": button_name,
                            "int_data": int_data,
                            "expected_value": expected_value
                        }
                        return result
                    else:
                        print(f"[按键测试] ❌ 30秒内匹配失败: 预期结果({expected_value}) != 实际结果({actual_value})，倒计时结束后自动勾选【异常】")
                else:
                    print(f"[按键测试] ⚠️ IO索引 {io_index} 超出范围，int_data长度: {len(int_data)}")
            else:
                # 超时未获取到数据，尝试从all_output中解析（支持多行，取最后一个非空的匹配）
                print("⚠️  订阅超时，未获取到有效的IO触发数据，尝试从完整输出解析...")
                int_data_matches = re.findall(r'int_data:\s*\[([0-9, \n]*)\]', all_output, re.MULTILINE | re.DOTALL)
                if int_data_matches:
                    # 从后往前查找，找到最后一个非空的int_data（避免空数组覆盖有效数据）
                    parsed_int_data = None
                    for int_data_str in reversed(int_data_matches):
                        # 移除换行符，保留空格（用于分割）
                        int_data_str_clean = int_data_str.replace('\n', ' ').strip()
                        if int_data_str_clean:  # 非空数组
                            parsed_int_data = [int(x.strip()) for x in int_data_str_clean.split(',') if x.strip()]
                            if parsed_int_data:  # 确保数组不为空
                                break  # 找到有效的int_data，退出循环
                    
                    if parsed_int_data:
                        int_data = parsed_int_data
                        print(f"🔍 从完整输出中解析到IO数据: {int_data}")
                        if len(int_data) > io_index:
                            actual_value = int_data[io_index]
                            expected_value = 0
                            print(f"[按键测试] 预期结果: {expected_value}")
                            print(f"[按键测试] 实际结果: {actual_value}")
                            
                            # 最终检查：如果实际值和预期值相等，应该返回成功
                            if actual_value == expected_value:
                                print(f"[按键测试] ✅ 最终匹配成功: 预期结果({expected_value}) == 实际结果({actual_value})，自动勾选【正常】")
                                result = {
                                    "status": "success",
                                    "io_value": actual_value,
                                    "test_status": "normal",
                                    "io_index": io_index,
                                    "button_name": button_name,
                                    "int_data": int_data,
                                    "expected_value": expected_value
                                }
                                return result
                            else:
                                print(f"[按键测试] ❌ 30秒内匹配失败: 预期结果({expected_value}) != 实际结果({actual_value})，倒计时结束后自动勾选【异常】")
            
            # 返回错误，让前端在超时后自动勾选异常
            return {"status": "error", "message": "30秒内未匹配成功，倒计时结束后自动勾选异常"}
                
        except paramiko.AuthenticationException:
            return {"status": "error", "message": "SSH认证失败"}
        except paramiko.SSHException as e:
            return {"status": "error", "message": f"SSH连接错误: {str(e)}"}
        except TimeoutError:
            print(f"⏰ 订阅超时（{timeout}秒），已停止")
            return {"status": "error", "message": f"订阅超时（{timeout}秒），未获取到有效数据"}
        except Exception as e:
            return {"status": "error", "message": f"检查错误: {str(e)}"}
        finally:
            # 关闭通道和SSH连接（确保一定会关闭）
            if channel:
                try:
                    channel.close()
                except:
                    pass
            try:
                ssh.close()
            except:
                pass
            print("🔌 SSH连接已关闭")
