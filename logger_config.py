# 日志配置模块
import os
import sys
from datetime import datetime
import logging
from logging.handlers import RotatingFileHandler

# 日志根目录
LOG_ROOT = os.path.join(os.path.dirname(__file__), 'logs')

# 确保日志目录存在
if not os.path.exists(LOG_ROOT):
    os.makedirs(LOG_ROOT)

# 获取当前日期（用于创建日期文件夹）
current_date = datetime.now().strftime('%Y-%m-%d')
date_folder = os.path.join(LOG_ROOT, current_date)

# 确保日期文件夹存在
if not os.path.exists(date_folder):
    os.makedirs(date_folder)

# 获取当前时间（用于日志文件名）
current_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
log_filename = f'{current_time}.txt'
log_filepath = os.path.join(date_folder, log_filename)

# 配置日志格式
log_format = '%(asctime)s [%(levelname)s] %(message)s'
date_format = '%Y-%m-%d %H:%M:%S'

# 创建logger
logger = logging.getLogger('RobotTest')
logger.setLevel(logging.DEBUG)

# 避免重复添加handler
if not logger.handlers:
    # 文件handler（追加模式，带轮转）
    file_handler = RotatingFileHandler(
        log_filepath,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(log_format, date_format)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # 注意：不添加控制台handler，因为PrintLogger会直接输出到控制台
    # 这样可以避免重复打印

# 保存原始的stdout
_original_stdout = sys.stdout

# 重定向print到logger
class PrintLogger:
    """将print输出重定向到logger（只记录到文件，控制台直接输出）"""
    def __init__(self, logger, original_stdout):
        self.logger = logger
        self.terminal = original_stdout
        self.buffer = ''
        # 确保所有必要的属性都存在，兼容Flask/click库
        self._stream = original_stdout
    
    def write(self, message):
        if not message:
            return
        
        # 保存到缓冲区
        self.buffer += message
        
        # 如果遇到换行符，记录完整行
        if '\n' in self.buffer or '\r' in self.buffer:
            lines = self.buffer.splitlines(True)
            self.buffer = lines[-1] if lines else ''
            
            for line in lines[:-1]:
                line = line.rstrip('\n\r')
                if line.strip():  # 只记录非空消息
                    # 只记录到日志文件（带时间戳），不输出到控制台
                    # 因为terminal.write会在下面统一输出，避免重复
                    self.logger.info(line)
        
        # 直接输出到控制台（保持原有print的显示效果，不带时间戳）
        # 注意：这里只输出原始消息，不通过logger，避免重复
        if hasattr(self.terminal, 'write'):
            self.terminal.write(message)
    
    def flush(self):
        if hasattr(self.terminal, 'flush'):
            self.terminal.flush()
        # 如果缓冲区有内容，也记录到文件
        if self.buffer.strip():
            self.logger.info(self.buffer.rstrip('\n\r'))
            self.buffer = ''
    
    def __getattr__(self, name):
        # 代理所有其他属性到原始stdout，确保兼容性
        return getattr(self.terminal, name)

# 重定向stdout
sys.stdout = PrintLogger(logger, _original_stdout)

# 记录启动信息（使用logger.info，这样会同时写入文件和控制台）
logger.info('=' * 60)
logger.info('机器人静态测试系统 - 日志系统启动')
logger.info(f'日志文件: {log_filepath}')
logger.info('=' * 60)
