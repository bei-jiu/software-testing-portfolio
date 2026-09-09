# ==================== 设备连接信息 ====================
# MuMu 模拟器在 adb 里的设备名
DEVICE_UDID = "emulator-5554"

# Appium Server 地址
APPIUM_SERVER = "http://127.0.0.1:4723"

# ==================== 被测应用：拼多多 ====================
APP_PACKAGE = "com.xunmeng.pinduoduo"
APP_ACTIVITY = ".ui.activity.MainFrameActivity"

# 搜索的商品关键词
SEARCH_KEYWORD = "手机"

# 截图保存目录
SCREENSHOT_DIR = "screenshots"

# ==================== 兼容性回归用：待测设备列表 ====================
# 现在只有一台 MuMu 模拟器；以后接真机，把真机的 adb 设备名加进来即可，
# 比如 ["emulator-5554", "R58M3XXXXX", "ABCDEFGHIJ"]
DEVICE_LIST = ["emulator-5554"]
