import os
import re
import subprocess
import time

from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config import DEVICE_UDID, SCREENSHOT_DIR, SEARCH_KEYWORD

PKG = "com.xunmeng.pinduoduo"
ADB = r"C:\android-sdk\platform-tools\adb.exe"

# ==================== 坐标（竖屏 900×1600；改了模拟器分辨率需重抓）====================
POS_FIRST_PRODUCT = (450, 350)   # 搜索结果第一个商品卡片中心
POS_FIRST_SIMILAR = (224, 760)   # 售罄页「相似商品」第一个（左列）
POS_COLLECT = (162, 1547)        # 详情页底部「收藏」按钮
POS_TAB_PROFILE = (810, 1563)    # 首页底部导航「个人中心」
POS_MY_FAVORITES = (90, 408)     # 个人中心「商品收藏」入口
POS_FAV_MANAGE = (861, 69)       # 收藏列表右上角「管理」
POS_FAV_CHECK = (31, 254)        # 管理模式下第一个商品的勾选按钮
POS_FAV_DELETE = (795, 1560)     # 管理模式底部「删除」
POS_DELETE_CONFIRM = (558, 833)  # 删除确认弹窗里的「删除」
POS_ORDER_TAB = (90, 306)        # 个人中心「待付款」订单入口

# 详情页独有的文字（搜索结果页没有），用来确认真的进到了详情页
DETAIL_MARKERS = ("直接拼成", "全场包邮", "7天无理由退货", "拼单即将结束")


# ==================== 纯 adb 工具（绕开 uiautomator，避免卡顿）====================


def _adb(*args):
    """执行 adb 命令，返回 stdout 字符串（UTF-8）。"""
    r = subprocess.run([ADB, "-s", DEVICE_UDID, *args], capture_output=True)
    return r.stdout.decode("utf-8", errors="replace")


def _tap(x, y):
    """adb 坐标点击，不经过 uiautomator，不会卡。"""
    _adb("shell", "input", "tap", str(x), str(y))


def _swipe_up(times=1):
    """adb 上滑，加载更多内容。"""
    for _ in range(times):
        _adb("shell", "input", "swipe", "450", "1200", "450", "400", "300")


def _top_activity():
    """adb 读当前最顶层 Activity（含包名）。闪退后会变成桌面 launcher。"""
    out = _adb("shell", "dumpsys", "activity", "activities")
    for line in out.splitlines():
        if "topResumedActivity" in line:
            # 形如：topResumedActivity=ActivityRecord{... u0 com.xunmeng.pinduoduo/.activity.NewPageActivity ...}
            m = re.search(r"u0\s+(\S+?)/", line)
            if m:
                return m.group(1)
    return None


def _shot_adb(name):
    """adb 直接截图，不经过 uiautomator。"""
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    path = os.path.join(SCREENSHOT_DIR, name)
    with open(path, "wb") as f:
        subprocess.run([ADB, "-s", DEVICE_UDID, "exec-out", "screencap", "-p"], stdout=f)
    return path


def _on_detail(driver):
    """用页面文字判断当前是否在商品详情页。"""
    return any(m in driver.page_source for m in DETAIL_MARKERS)


def _go_home(driver):
    """按返回键直到回到首页（MainFrameActivity）。"""
    for _ in range(6):
        if driver.current_activity == ".ui.activity.MainFrameActivity":
            return
        _adb("shell", "input", "keyevent", "4")
        time.sleep(1.5)


# ==================== Appium 部分（搜索中文商品名，adb 输不了中文）====================


def _search(driver, wait, keyword):
    """搜索商品：点搜索框 → 输入关键词 → 回车。"""
    search_bar = wait.until(
        EC.element_to_be_clickable((AppiumBy.ACCESSIBILITY_ID, "搜索"))
    )
    search_bar.click()

    edit = wait.until(
        EC.presence_of_element_located((AppiumBy.CLASS_NAME, "android.widget.EditText"))
    )
    edit.send_keys(keyword)
    driver.execute_script("mobile: pressKey", {"keycode": 66})


def _enter_detail(driver):
    """点第一个商品进详情页；若该商品售罄跳到相似商品页，再点第一个相似商品。"""
    _tap(*POS_FIRST_PRODUCT)
    time.sleep(2)
    if _on_detail(driver):
        return
    _tap(*POS_FIRST_SIMILAR)
    time.sleep(2)


def _get_title(driver):
    """从详情页提取商品标题（去掉「【xx收藏】」前缀后取前 12 字）。"""
    m = re.search(r'text="(【[^"]*?收藏】[^"]{5,})"', driver.page_source)
    if not m:
        return None
    title = re.sub(r"^【[^】]*】", "", m.group(1))
    return title[:12]


# ==================== 用例 1：搜索商品 ====================


def test_search_product(driver):
    """启动拼多多 → 点搜索框 → 输入关键词 → 搜索 → 断言出现商品列表。"""
    wait = WebDriverWait(driver, 25)

    # 启动后首页出现搜索框
    wait.until(EC.element_to_be_clickable((AppiumBy.ACCESSIBILITY_ID, "搜索")))
    _shot_adb("pdd_search_01_home.png")

    # 搜索「手机」
    _search(driver, wait, SEARCH_KEYWORD)
    time.sleep(2)

    # 断言：页面出现商品列表（有价格 ¥ 或「券后」）
    src = driver.page_source
    assert "¥" in src or "券后" in src, "搜索结果页没有商品列表"
    _shot_adb("pdd_search_02_result.png")


# ==================== 用例 2：商品收藏 + 取消收藏 ====================


def test_collect_product(driver):
    """详情页点收藏 → 我的收藏页断言商品在列 → 取消收藏清理数据。"""
    wait = WebDriverWait(driver, 25)

    # 搜索进详情页
    wait.until(EC.element_to_be_clickable((AppiumBy.ACCESSIBILITY_ID, "搜索")))
    _search(driver, wait, SEARCH_KEYWORD)
    time.sleep(2)
    _enter_detail(driver)
    assert _on_detail(driver), "未进入商品详情页"
    title = _get_title(driver)
    _shot_adb("pdd_collect_01_detail.png")

    # 点收藏按钮
    _tap(*POS_COLLECT)
    time.sleep(1)
    assert "已收藏" in driver.page_source, "点收藏后按钮没有变成「已收藏」"
    _shot_adb("pdd_collect_02_collected.png")

    # 回首页 → 个人中心 → 商品收藏
    _go_home(driver)
    _tap(*POS_TAB_PROFILE)
    time.sleep(2)
    _tap(*POS_MY_FAVORITES)
    time.sleep(2)

    # 断言：该商品出现在收藏列表
    src = driver.page_source
    assert title and title in src, f"收藏列表里没有该商品：{title}"
    _shot_adb("pdd_collect_03_favlist.png")

    # 取消收藏清理：管理 → 勾选 → 删除 → 确认
    _tap(*POS_FAV_MANAGE)
    time.sleep(1)
    _tap(*POS_FAV_CHECK)
    time.sleep(1)
    _tap(*POS_FAV_DELETE)
    time.sleep(1)
    _tap(*POS_DELETE_CONFIRM)
    time.sleep(2)

    # 断言：收藏列表已清空
    assert "暂无收藏的商品" in driver.page_source, "取消收藏后列表没有清空"
    _shot_adb("pdd_collect_04_cleaned.png")


# ==================== 用例 4：浏览翻页（上滑加载更多）====================


def test_scroll_browse(driver):
    """搜索结果页循环上滑加载更多，检查页面不闪退、不卡死。"""
    wait = WebDriverWait(driver, 25)

    wait.until(EC.element_to_be_clickable((AppiumBy.ACCESSIBILITY_ID, "搜索")))
    _search(driver, wait, SEARCH_KEYWORD)
    time.sleep(2)

    # 上滑 5 次，每次检查应用还活着（顶层 Activity 还是拼多多的，没闪退回桌面）
    for i in range(5):
        _swipe_up()
        time.sleep(1)
        act = _top_activity()
        assert act == PKG, f"第 {i + 1} 次翻页后应用闪退/异常：{act}"
        print(f"第 {i + 1} 次翻页正常，顶层 Activity: {act}")

    _shot_adb("pdd_scroll_01_after_swipe.png")


# ==================== 用例 5：订单页面 ====================


def test_order_page(driver):
    """进入个人中心 → 我的订单，读取订单列表，校验订单状态文字。"""
    wait = WebDriverWait(driver, 25)

    # 启动 → 个人中心
    wait.until(EC.element_to_be_clickable((AppiumBy.ACCESSIBILITY_ID, "搜索")))
    _tap(*POS_TAB_PROFILE)
    time.sleep(2)
    _shot_adb("pdd_order_01_usercenter.png")

    # 点「待付款」进入我的订单
    _tap(*POS_ORDER_TAB)
    time.sleep(2)
    _shot_adb("pdd_order_02_orderlist.png")

    # 断言：订单状态 tab 文字存在（拼多多的订单状态：待付款/拼团中/打包中/待收货/评价）
    src = driver.page_source
    for status in ("待付款", "待收货"):
        assert status in src, f"订单页缺少状态文字：{status}"
    print("订单状态 tab 校验通过：待付款 / 待收货")

    # 上滑读取订单列表（当前账号无订单，会显示「没找到订单」的空状态）
    _swipe_up()
    time.sleep(1)
    _shot_adb("pdd_order_03_scrolled.png")


# ==================== 用例 6：兼容性回归 ====================


def test_compat_regression(driver):
    """核心流程回归：搜索 → 进详情，检查页面不错乱、不闪退。

    当前只有一台模拟器，直接跑。以后接多台真机做兼容性回归时，
    给每台设备各建一个 Appium 连接、分别跑一遍即可（设备名放 config.py 的 DEVICE_LIST）。
    """
    wait = WebDriverWait(driver, 25)

    wait.until(EC.element_to_be_clickable((AppiumBy.ACCESSIBILITY_ID, "搜索")))
    _search(driver, wait, SEARCH_KEYWORD)
    time.sleep(2)

    # 断言搜索出结果
    src = driver.page_source
    assert "¥" in src or "券后" in src, "搜索结果页没有商品"

    # 进详情页，断言详情页正常渲染
    _enter_detail(driver)
    assert _on_detail(driver), "详情页没有正常渲染"
    print(f"设备 {DEVICE_UDID} 核心流程通过")
    _shot_adb("pdd_compat_01_ok.png")
