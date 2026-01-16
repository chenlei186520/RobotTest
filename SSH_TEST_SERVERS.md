# SSH测试服务器信息

## 用于调试的SSH服务器

### 方法1：使用本地SSH服务器（推荐）

如果你有Linux系统或WSL，可以在本地启动SSH服务器：

1. **安装OpenSSH服务器**（Linux）：
   ```bash
   sudo apt-get install openssh-server
   sudo systemctl start ssh
   ```

2. **创建测试用户**：
   ```bash
   sudo useradd -m robot
   sudo passwd robot
   # 输入密码：robot
   ```

3. **测试连接**：
   ```bash
   ssh robot@localhost
   ```

4. **在URL中使用**：
   ```
   http://localhost:5000/api/devicetest?carip=localhost&vehiclemodel=X100
   ```

### 方法2：使用Docker SSH服务器（推荐）

1. **运行测试SSH服务器容器**：
   ```bash
   docker run -d -p 2222:22 -e SSH_USER=robot -e SSH_PASSWORD=robot panubo/sshd
   ```

2. **在URL中使用**：
   ```
   http://localhost:5000/api/devicetest?carip=localhost&vehiclemodel=X100
   ```
   注意：需要在config.py中设置SSH端口为2222（如果使用非标准端口）

### 方法3：使用公开的测试SSH服务器

**注意**：这些服务器通常不允许执行命令，仅用于测试连接。

- **test.rebex.net**
  - 用户名：demo
  - 密码：password
  - 端口：22
  - **限制**：只读访问，不能执行命令

### 方法4：使用虚拟机

1. 在VirtualBox或VMware中创建Linux虚拟机
2. 配置SSH服务
3. 设置用户名为robot，密码为robot
4. 获取虚拟机IP地址
5. 在URL中使用该IP

## 调试步骤

1. **检查paramiko是否安装**：
   ```bash
   pip install paramiko
   ```

2. **测试SSH连接**（在Python中）：
   ```python
   import paramiko
   ssh = paramiko.SSHClient()
   ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
   ssh.connect('your_ip', username='robot', password='robot')
   print("连接成功！")
   ssh.close()
   ```

3. **查看Flask控制台输出**：
   - 代码中已添加详细的调试日志
   - 查看终端/控制台的 `[SSH调试]` 输出

4. **检查常见问题**：
   - IP地址是否正确
   - 用户名和密码是否正确（config.py中）
   - SSH服务是否运行
   - 防火墙是否阻止连接
   - 网络是否可达

## 配置说明

在 `config.py` 中修改SSH配置：
```python
SSH_USER = "robot"      # 修改为实际的SSH用户名
SSH_PASSWORD = "robot" # 修改为实际的SSH密码
SSH_TIMEOUT = 10        # 连接超时时间（秒）
```
