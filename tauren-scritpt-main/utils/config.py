"""
配置管理模块
"""
import os
import yaml
import logging

class Config:
    """配置管理类"""
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, config_file="config/config.yaml"):
        if not hasattr(self, "_initialized"):
            self.config_file = config_file
            self.config = self._load_config()
            self._initialized = True
    
    def _load_config(self):
        """加载配置文件"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                logging.info("配置文件加载成功: %s", self.config_file)
                return config
            else:
                logging.error("配置文件不存在: %s", self.config_file)
                return self._get_default_config()
        except Exception as e:
            logging.error("加载配置文件失败: %s", str(e))
            return self._get_default_config()
    
    def _get_default_config(self):
        """获取默认配置"""
        return {
            "operation": {
                "min_delay": 2,
                "max_delay": 4,
                "max_retries": 2,
                "max_links_per_cycle": 10,
                "browser": {
                    "headless": False,
                    "maximize": True
                },
                "cycle": {
                    "max_cycles": 5,
                    "cycle_interval": 3600,
                    "users_per_cycle": 10,
                    "videos_per_user": 5
                }
            },
            "logging": {
                "level": "INFO",
                "log_dir": "logs"
            }
        }
    
    def get(self, key, default=None):
        """获取配置值"""
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
    

    
    def get_operation_config(self):
        """获取操作配置"""
        return self.get("operation", {})
    
    def get_logging_config(self):
        """获取日志配置"""
        return self.get("logging", {})
    
    def reload(self):
        """重新加载配置文件"""
        self.config = self._load_config()
        logging.info("配置文件已重新加载: %s", self.config_file)
    
    def save_config(self, new_config):
        """保存配置到文件"""
        try:
            # 合并配置，保留未修改的项
            def merge_config(old, new):
                for k, v in new.items():
                    if isinstance(v, dict) and k in old and isinstance(old[k], dict):
                        merge_config(old[k], v)
                    else:
                        old[k] = v
            
            merge_config(self.config, new_config)
            
            # 确保配置目录存在
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            
            # 写入配置文件
            with open(self.config_file, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, default_flow_style=False, allow_unicode=True)
            
            logging.info("配置文件保存成功: %s", self.config_file)
            return True
        except Exception as e:
            logging.error("保存配置文件失败: %s", str(e))
            return False

# 全局配置实例
config = Config()