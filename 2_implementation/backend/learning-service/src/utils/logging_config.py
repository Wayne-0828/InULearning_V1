"""
日誌配置工具

提供統一的日誌配置和格式化
"""

import os
import logging
import logging.config
from datetime import datetime


def setup_logging():
    """設置日誌配置"""
    
    # 日誌級別
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    
    # 日誌格式
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    
    # 日誌配置
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": log_format,
                "datefmt": date_format,
            },
            "detailed": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s",
                "datefmt": date_format,
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": log_level,
                "formatter": "default",
                "stream": "ext://sys.stdout",
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": log_level,
                "formatter": "detailed",
                "filename": "logs/learning-service.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
            },
        },
        "loggers": {
            "": {
                "level": log_level,
                "handlers": ["console", "file"],
                "propagate": False,
            },
            "uvicorn": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False,
            },
            "sqlalchemy": {
                "level": "WARNING",
                "handlers": ["console"],
                "propagate": False,
            },
        },
    }
    
    # 創建日誌目錄
    os.makedirs("logs", exist_ok=True)
    
    # 應用配置
    logging.config.dictConfig(logging_config)
    
    # 設置根日誌器
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured with level: {log_level}")


def get_logger(name: str) -> logging.Logger:
    """獲取指定名稱的日誌器"""
    return logging.getLogger(name)


class RequestLogger:
    """請求日誌記錄器"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
    
    def log_request(self, method: str, path: str, user_id: str = None, **kwargs):
        """記錄請求日誌"""
        self.logger.info(
            f"Request: {method} {path} | User: {user_id or 'anonymous'} | "
            f"Params: {kwargs}"
        )
    
    def log_response(self, method: str, path: str, status_code: int, 
                    response_time: float, user_id: str = None):
        """記錄回應日誌"""
        self.logger.info(
            f"Response: {method} {path} | Status: {status_code} | "
            f"Time: {response_time:.3f}s | User: {user_id or 'anonymous'}"
        )
    
    def log_error(self, method: str, path: str, error: Exception, 
                  user_id: str = None):
        """記錄錯誤日誌"""
        self.logger.error(
            f"Error: {method} {path} | Error: {str(error)} | "
            f"User: {user_id or 'anonymous'}",
            exc_info=True
        ) 