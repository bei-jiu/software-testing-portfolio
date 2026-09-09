import os
import subprocess
import sys
import time

# 把项目根目录（pdd_test）加入 sys.path，保证 from config import ... 能导入
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import pytest
from appium import webdriver
from appium.options.android import UiAutomator2Options

from config import APP_ACTIVITY, APP_PACKAGE, APPIUM_SERVER, DEVICE_UDID

ADB = r"C:\android-sdk\platform-tools\adb.exe"


@pytest.fixture(scope="session")
def driver():
    """整个测试会话只建一次 Appium 连接，所有用例共用。

    以前是 scope="function"（每个用例都重新 webdriver.Remote 连一次，很慢），
    改成 session 后只连一次，几个用例共享，省掉反复重连的时间。
    这里不指定 app_package，所以建连接时不会自动启动 App；
    App 的启动交给下面 _restart_app 在每个用例前做。
    """
    options = UiAutomator2Options()
    options.platform_name = "Android"
    options.automation_name = "UiAutomator2"
    options.device_name = DEVICE_UDID
    options.udid = DEVICE_UDID
    # 命令超时设长一点，避免页面偶发卡顿就把会话关掉
    options.new_command_timeout = 180

    d = webdriver.Remote(APPIUM_SERVER, options=options)
    d.implicitly_wait = 10
    yield d
    d.quit()


@pytest.fixture(scope="function", autouse=True)
def _restart_app():
    """每个用例前强制重启 App，保证干净起点（用例隔离）。

    注意：这里只重启 App（adb force-stop + monkey 启动），
    不重建 Appium 连接——所以比原来快。
    """
    subprocess.run(
        [ADB, "-s", DEVICE_UDID, "shell", "am", "force-stop", APP_PACKAGE],
        capture_output=True,
    )
    subprocess.run(
        [ADB, "-s", DEVICE_UDID, "shell", "monkey",
         "-p", APP_PACKAGE, "-c", "android.intent.category.LAUNCHER", "1"],
        capture_output=True,
    )
    time.sleep(4)  # 等首页加载完
    yield
