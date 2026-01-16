# 灯光测试API处理器

from .base_api import BaseAPI
import config

class LightAPI(BaseAPI):
    """灯光测试专用的API处理器"""
    
    @staticmethod
    def send_command(item_id, ssh_host=None, ssh_user=None, ssh_password=None):
        """发送灯光控制指令（通过SSH）"""
        # 如果是关闭所有灯的特殊指令
        if item_id == 'turn_off_all_lights':
            return BaseAPI.send_command(item_id, {'turn_off_all_lights': config.TURN_OFF_ALL_LIGHTS_COMMAND}, ssh_host, ssh_user, ssh_password)
        # 其他灯光指令
        return BaseAPI.send_command(item_id, config.COMMAND_MAP, ssh_host, ssh_user, ssh_password)
    
    @staticmethod
    def check_io(item_id, ssh_host=None, ssh_user=None, ssh_password=None):
        """检查灯光IO状态（通过SSH执行rostopic命令）"""
        import config
        return BaseAPI.check_io(
            item_id,
            config.IO_INDEX_MAP,
            config.ROS_TOPIC,
            config.ROS_COMMAND_TIMEOUT,
            config.IO_CHECK_TIMEOUT,
            ssh_host,
            ssh_user,
            ssh_password
        )
