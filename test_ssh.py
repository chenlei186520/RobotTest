#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SSH连接测试脚本
用于测试SSH配置是否正确
"""

import sys
import config

def test_ssh_connection(ssh_host, ssh_user=None, ssh_password=None):
    """测试SSH连接"""
    ssh_user = ssh_user or config.SSH_USER
    ssh_password = ssh_password or config.SSH_PASSWORD
    
    print(f"正在测试SSH连接...")
    print(f"主机: {ssh_host}")
    print(f"用户名: {ssh_user}")
    print(f"密码: {'*' * len(ssh_password)}")
    print("-" * 50)
    
    try:
        import paramiko
        
        # 创建SSH客户端
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # 连接SSH服务器
        print("正在连接...")
        ssh.connect(
            hostname=ssh_host,
            username=ssh_user,
            password=ssh_password,
            timeout=config.SSH_TIMEOUT,
            look_for_keys=False,
            allow_agent=False
        )
        print("✓ SSH连接成功！")
        
        # 测试执行命令
        print("\n正在测试命令执行...")
        test_command = "echo 'SSH测试成功'"
        stdin, stdout, stderr = ssh.exec_command(test_command, timeout=config.SSH_TIMEOUT)
        exit_status = stdout.channel.recv_exit_status()
        
        if exit_status == 0:
            output = stdout.read().decode('utf-8').strip()
            print(f"✓ 命令执行成功！")
            print(f"输出: {output}")
        else:
            error = stderr.read().decode('utf-8').strip()
            print(f"✗ 命令执行失败: {error}")
        
        # 关闭连接
        ssh.close()
        print("\n✓ 测试完成！SSH配置正确。")
        return True
        
    except paramiko.AuthenticationException:
        print("✗ SSH认证失败：用户名或密码错误")
        print(f"  请检查config.py中的配置：")
        print(f"  SSH_USER = '{config.SSH_USER}'")
        print(f"  SSH_PASSWORD = '{config.SSH_PASSWORD}'")
        return False
    except paramiko.SSHException as e:
        print(f"✗ SSH连接错误: {str(e)}")
        print("  可能的原因：")
        print("  1. SSH服务器未运行")
        print("  2. IP地址不正确")
        print("  3. 网络不可达")
        return False
    except paramiko.socket.timeout:
        print(f"✗ SSH连接超时（{config.SSH_TIMEOUT}秒）")
        print("  可能的原因：")
        print("  1. IP地址不正确")
        print("  2. 网络不可达")
        print("  3. 防火墙阻止连接")
        return False
    except ImportError:
        print("✗ 错误：未安装paramiko库")
        print("  请运行: pip install paramiko")
        return False
    except Exception as e:
        print(f"✗ 发生错误: {str(e)}")
        print(f"  错误类型: {type(e).__name__}")
        return False

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python test_ssh.py <SSH_IP地址>")
        print("示例: python test_ssh.py 10.26.7.70")
        print("示例: python test_ssh.py localhost")
        sys.exit(1)
    
    ssh_host = sys.argv[1]
    success = test_ssh_connection(ssh_host)
    sys.exit(0 if success else 1)
