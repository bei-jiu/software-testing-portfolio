# shop_test — 简易接口自动化测试项目（登录接口）

一个最小但完整可运行的接口自动化测试框架，演示测试开发的核心知识点：
请求封装、日志、数据驱动、断言、pytest 参数化。

当前测试对象：**ShopXO 商城登录接口**。

## 项目结构

```
shop_test/
├── conftest.py              # 把项目根目录加入 sys.path，保证 import 正常
├── config.py                # 全局配置（接口地址、请求头）
├── common.py                # 日志工具 + HTTP 请求封装（Logger + Request）
├── generate_report.py       # 一键生成中文版 Allure 报告
├── pytest.ini               # pytest 配置
├── data/
│   └── login_data.yaml      # 登录测试数据（数据驱动）
└── testcases/
    └── test_login.py        # 登录测试用例（pytest）
```

## 环境准备

```bash
pip install requests pytest pyyaml
```

## 运行

```bash
cd shop_test
python -m pytest
```

预期输出：`4 passed`。

## 生成 Allure 报告

前提：需要 Java 环境（8 及以上）。

1. 安装插件：
   ```bash
   pip install allure-pytest
   ```
2. 下载 [Allure 命令行工具](https://github.com/allure-framework/allure2/releases) 并解压，得到 `bin/allure.bat`。
3. 运行测试（`pytest.ini` 已配置自动生成 allure 结果到 `allure-results/`）：
   ```bash
   python -m pytest
   ```
4. 生成 HTML 报告：
   ```bash
   allure generate allure-results -o allure-report --clean
   ```
5. 打开报告：
   ```bash
   allure open allure-report
   ```

> `allure-results/` 和 `allure-report/` 已加入 `.gitignore`，不会提交进仓库。

### 中文版报告

Allure 2.46 已内置中文翻译，两种方式切换到中文：

1. **报告右上角的语言切换器**（点开选「中文」）。
2. 直接运行 `python generate_report.py`，一键生成默认中文的报告（等价于 `allure generate` + 自动改 `<html lang="zh">`）。

## 被测接口说明

- **接口**：`POST http://shop-xo.hctestedu.com/index.php?s=/index/user/login.html`
- **请求头**：必须带 `X-Requested-With: XMLHttpRequest`，否则返回 HTML 而不是 JSON
- **请求体（表单）**：`accounts`（账号）、`pwd`（密码 6~18 位）、`type=username`
- **返回格式**：`{"msg": "...", "code": <int>, "data": ...}`

| code | 含义 |
|------|------|
| 0    | 登录成功 |
| -1   | 账号为空 |
| -3   | 账号不存在 |
| -4   | 密码错误 |

- **测试账号**：`admin` / `123456`

## 换成你自己的业务接口

1. 修改 `config.py` 里的 `HOST` 和接口地址。
2. 在 `testcases/` 里按你的接口字段改写断言（比如校验 `code`、`token`）。
3. 在 `data/` 里补充测试数据，`@pytest.mark.parametrize` 会自动为每条数据生成用例。

## 知识点对照

| 知识点     | 体现位置 |
|-----------|---------|
| 接口测试   | `common.py` 里用 requests 发 GET/POST |
| 日志       | `common.py` 里 Logger + Request 自动记录请求/响应 |
| 数据驱动   | `data/login_data.yaml` + `@pytest.mark.parametrize` |
| 断言       | `test_login.py` 里 `assert` 校验状态码、业务码、字段 |
| 封装复用   | `Request` 类统一封装请求和日志 |
| 测试框架   | pytest 管理用例、参数化 |

## 说明

- 日志会同时输出到控制台和 `logs/test.log`。若在 Windows 的 cmd 里中文显示乱码，可先执行 `chcp 65001` 切换到 UTF-8。
