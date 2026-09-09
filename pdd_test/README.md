# 拼多多 App 移动端自动化测试框架

基于 **Python + pytest + Appium** 的拼多多 Android 客户端 UI 自动化测试项目，覆盖商品搜索、收藏、浏览翻页、订单页面等核心业务场景，并支持多设备兼容性回归。

## 技术栈

- **语言/框架**：Python 3、pytest、pytest-allure（报告）
- **移动自动化**：Appium 3.x + UiAutomator2 驱动、Appium-Python-Client
- **辅助工具**：Android Debug Bridge（adb）、模拟器（MuMu）
- **设计模式**：Page Object 思想 + fixture 用例隔离 + 数据驱动（设备参数化）

## 测试用例

| 用例 | 场景 | 覆盖点 |
|------|------|--------|
| test_search_product | 搜索商品 | 首页搜索、关键词输入、结果列表断言 |
| test_collect_product | 商品收藏 | 收藏 → 收藏列表校验 → 取消收藏清理数据 |
| test_scroll_browse | 浏览翻页 | 循环上滑加载更多、闪退/卡顿检测 |
| test_order_page | 订单页面 | 订单状态文字校验（待付款/待收货） |
| test_compat_regression | 兼容性回归 | 核心流程在多设备上回归 |

## 项目亮点

1. **破解控件 ID 混淆**：拼多多所有资源 ID 都被混淆成同一个 `:id/pdd`，通过 content-desc、text、坐标点等多种定位策略组合，保证元素稳定定位。
2. **adb 直连绕开 UIAutomator**：对动态加载、易卡顿的页面，改用 adb 坐标点击 + `dumpsys` 状态校验，避免 UI 自动化常见的元素找不到/超时问题。
3. **完整的测试数据清理**：收藏用例执行后自动取消收藏，保证测试不污染真实账号数据。
4. **用例隔离 + 会话复用**：每个用例重启 App 保证独立可重复，同时 Appium 会话只建一次，整体提速约 36%。
5. **闪退自动检测**：翻页时通过 `dumpsys activity` 校验顶层 Activity，自动发现应用闪退/崩溃。
6. **多设备兼容回归**：设备列表参数化，接真机即可在每台设备上自动回归核心流程。
7. **全程截图留证**：每一步操作都保存截图，失败时可快速定位问题。

## 项目结构

```
pdd_test/
├── config.py          # 设备信息、被测应用、搜索关键词、设备列表
├── conftest.py        # Appium 会话（session 级复用）+ 用例隔离 fixture
├── pytest.ini         # pytest 配置
├── testcases/
│   └── test_pdd.py    # 5 个测试用例
├── screenshots/       # 每步操作的截图留证
├── run.bat            # 一键启动脚本（双击运行）
└── README.md
```

## 运行方式

### 方式一：一键启动（推荐）

双击 `run.bat`，脚本会自动完成：检查模拟器 → 检查/启动 Appium → 跑全部用例。

- 想只跑某一个用例：在项目目录命令行执行 `run.bat -k collect`（`collect` 可换成 `search` / `scroll` / `order` / `compat`）。

### 方式二：手动命令行

```bash
# 前置：启动 Appium Server 和 MuMu 模拟器
cd pdd_test
python -m pytest -v -s               # 跑全部用例
python -m pytest -k collect -v -s    # 只跑收藏用例
```
