import logging
import os
from logging.handlers import RotatingFileHandler

import requests


# ==================== 日志工具 ====================

class Logger:
    """日志工具类：提供统一的 logger 实例，同时输出到控制台和 logs/test.log"""

    def __init__(self):
        self.logger = logging.getLogger("shop_test")
        self.logger.setLevel(logging.INFO)

        # 避免重复添加 handler
        if not self.logger.handlers:
            formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

            # 控制台输出
            console = logging.StreamHandler()
            console.setFormatter(formatter)
            self.logger.addHandler(console)

            # 文件输出（logs/test.log，1MB 轮转，保留 3 份）
            log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
            os.makedirs(log_dir, exist_ok=True)
            file_handler = RotatingFileHandler(
                os.path.join(log_dir, "test.log"),
                maxBytes=1024 * 1024,
                backupCount=3,
                encoding="utf-8",
            )
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

    def getlog(self):
        return self.logger


# 模块级单例，供外部 from common import logger 使用
logger = Logger()


# ==================== HTTP 请求封装 ====================

class Request:
    """HTTP 请求封装：统一在请求前后记录日志"""

    log = logger.getlog()

    def get(self, url, **kwargs):
        self.log.info("准备发起 GET 请求，url: " + url)
        self.log.info("接口信息：{}".format(kwargs))
        r = requests.get(url=url, **kwargs)
        self.log.info("接口响应状态码：{}".format(r.status_code))
        self.log.info("接口响应内容：{}".format(r.text))
        return r

    def post(self, url, **kwargs):
        self.log.info("准备发起 POST 请求，url: " + url)
        self.log.info("接口信息：{}".format(kwargs))
        r = requests.post(url=url, **kwargs)
        self.log.info("接口响应状态码：{}".format(r.status_code))
        self.log.info("接口响应内容：{}".format(r.text))
        return r
