# 测试数据模块
# 自动加载所有测试数据

from .light_test import LIGHT_TEST_DATA
from .voice_test import VOICE_TEST_DATA
from .button_test import BUTTON_TEST_DATA
from .touch_test import TOUCH_TEST_DATA
from .display_test import DISPLAY_TEST_DATA
from .camera_test import CAMERA_TEST_DATA
from .lift_motor_test import LIFT_MOTOR_TEST_DATA
from .rotation_motor_test import ROTATION_MOTOR_TEST_DATA
from .walking_motor_test import WALKING_MOTOR_TEST_DATA

# 测试类别列表
TEST_CATEGORIES = [
    {"id": "light", "name": "灯光测试"},
    {"id": "voice", "name": "语音测试"},
    {"id": "button", "name": "按键测试"},
    {"id": "touch", "name": "触边测试"},
    {"id": "display", "name": "显示屏测试"},
    {"id": "camera", "name": "相机/激光/TOF测试"},
    {"id": "lift_motor", "name": "举升电机测试"},
    {"id": "rotation_motor", "name": "旋转电机测试"},
    {"id": "walking_motor", "name": "行走电机测试"},
]

# 所有测试详情数据
TEST_DETAILS = {
    "light": LIGHT_TEST_DATA,
    "voice": VOICE_TEST_DATA,
    "button": BUTTON_TEST_DATA,
    "touch": TOUCH_TEST_DATA,
    "display": DISPLAY_TEST_DATA,
    "camera": CAMERA_TEST_DATA,
    "lift_motor": LIFT_MOTOR_TEST_DATA,
    "rotation_motor": ROTATION_MOTOR_TEST_DATA,
    "walking_motor": WALKING_MOTOR_TEST_DATA,
}
