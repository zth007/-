"""
日志管理模块
"""
import os
import logging
from datetime import datetime

# 确保日志目录存在
log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# 配置日志
log_file = os.path.join(log_dir, f"toutiao_{datetime.now().strftime('%Y-%m-%d')}.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def log_login_operation(success, message):
    """记录登录操作"""
    if success:
        logger.info(f"登录成功: {message}")
    else:
        logger.error(f"登录失败: {message}")

def log_follow_operation(success, message):
    """记录关注操作"""
    if success:
        logger.info(f"关注成功: {message}")
    else:
        logger.error(f"关注失败: {message}")

def log_recommend_operation(success, message):
    """记录推荐操作"""
    if success:
        logger.info(f"推荐操作成功: {message}")
    else:
        logger.error(f"推荐操作失败: {message}")


def log_like_operation(link, success, message):
    """记录点赞操作"""
    if success:
        logger.info(f"点赞成功: {link} - {message}")
    else:
        logger.error(f"点赞失败: {link} - {message}")