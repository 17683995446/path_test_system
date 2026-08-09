"""
增强日志系统
======================================================================

结构化日志、彩色输出、分级管理
"""

import logging
import sys
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path


class ColoredFormatter(logging.Formatter):
    """彩色格式化器"""
    
    COLORS = {
        'DEBUG': '\033[36m',      # 青色
        'INFO': '\033[32m',       # 绿色
        'WARNING': '\033[33m',    # 黄色
        'ERROR': '\033[31m',      # 红色
        'CRITICAL': '\033[35m',   # 品红色
        'RESET': '\033[0m'
    }
    
    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset = self.COLORS['RESET']
        
        record.levelname = f"{color}{record.levelname}{reset}"
        return super().format(record)


class StructuredLogger:
    """结构化日志系统"""
    
    def __init__(
        self,
        name: str = "path_test_system",
        level: int = logging.INFO,
        log_file: Optional[str] = None,
        colored_output: bool = True
    ):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.logger.handlers = []
        
        # 控制台输出
        console_handler = logging.StreamHandler(sys.stdout)
        if colored_output:
            formatter = ColoredFormatter(
                '%(asctime)s | %(levelname)-15s | %(message)s',
                datefmt='%H:%M:%S'
            )
        else:
            formatter = logging.Formatter(
                '%(asctime)s | %(levelname)-15s | %(message)s',
                datefmt='%H:%M:%S'
            )
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # 文件输出
        if log_file:
            file_formatter = logging.Formatter(
                '%(asctime)s | %(levelname)-15s | %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)
        
        self.structured_logs: list = []
    
    def debug(self, message: str, **kwargs: Any) -> None:
        """调试日志"""
        self.logger.debug(message)
        self._log_structured('DEBUG', message, kwargs)
    
    def info(self, message: str, **kwargs: Any) -> None:
        """信息日志"""
        self.logger.info(message)
        self._log_structured('INFO', message, kwargs)
    
    def warning(self, message: str, **kwargs: Any) -> None:
        """警告日志"""
        self.logger.warning(message)
        self._log_structured('WARNING', message, kwargs)
    
    def error(self, message: str, **kwargs: Any) -> None:
        """错误日志"""
        self.logger.error(message)
        self._log_structured('ERROR', message, kwargs)
    
    def critical(self, message: str, **kwargs: Any) -> None:
        """严重日志"""
        self.logger.critical(message)
        self._log_structured('CRITICAL', message, kwargs)
    
    def _log_structured(self, level: str, message: str, extra: Dict[str, Any]) -> None:
        """结构化记录"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'level': level,
            'message': message,
            'extra': extra
        }
        self.structured_logs.append(entry)
    
    def get_structured_logs(self, limit: int = 100) -> list:
        """获取结构化日志"""
        return self.structured_logs[-limit:]


def create_structured_logger(
    name: str = "path_test_system",
    log_file: Optional[str] = None,
    level: int = logging.INFO
) -> StructuredLogger:
    """创建结构化日志器"""
    return StructuredLogger(name, level, log_file)


if __name__ == "__main__":
    logger = create_structured_logger()
    logger.info("✅ 日志系统初始化成功")
    logger.debug("调试信息")
    logger.warning("警告信息")
    logger.error("错误信息")
