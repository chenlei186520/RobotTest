# API模块初始化
# 统一导出所有API处理器

from .light_api import LightAPI
from .voice_api import VoiceAPI
from .button_api import ButtonAPI
from .camera_api import CameraAPI
from .lift_motor_api import LiftMotorAPI
from .rotation_motor_api import RotationMotorAPI
from .walking_motor_api import WalkingMotorAPI
from .base_api import BaseAPI

# API处理器映射
API_HANDLERS = {
    "light": LightAPI,
    "voice": VoiceAPI,
    "button": ButtonAPI,
    "touch": ButtonAPI,  # 触边测试使用按键测试的逻辑
    "display": ButtonAPI,  # 显示屏测试使用按键测试的逻辑
    "camera": CameraAPI,  # 相机/激光/TOF测试
    "lift_motor": LiftMotorAPI,  # 举升电机测试
    "rotation_motor": RotationMotorAPI,  # 旋转电机测试
    "walking_motor": WalkingMotorAPI,  # 行走电机测试
    # 其他测试类别可以在这里添加
    # ...
}

def get_api_handler(test_id):
    """根据测试ID获取对应的API处理器"""
    return API_HANDLERS.get(test_id, BaseAPI)
