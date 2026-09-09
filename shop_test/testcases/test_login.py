import os

import pytest
import yaml

from common import Request
from config import AJAX_HEADERS, LOGIN_URL

req = Request()

# 测试数据文件路径（用绝对路径，避免运行目录不同导致找不到文件）
DATA_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data",
    "login_data.yaml",
)


def load_data():
    """读取 yaml 测试数据"""
    with open(DATA_FILE, encoding="utf-8") as f:
        return yaml.safe_load(f)


@pytest.mark.parametrize("case", load_data())

def test_login(case):
    # 发送登录请求：data= 表示表单提交，headers 带 AJAX 头才会返回 JSON
    r = req.post(url=LOGIN_URL, data=case["data"], headers=AJAX_HEADERS)

    # 断言 1：HTTP 状态码正确
    assert r.status_code == 200, f"HTTP 状态码错误：{r.status_code}"

    # 断言 2：业务返回码正确
    resp = r.json()
    assert resp["code"] == case["expect_code"], \
        f"{case['name']} 失败：期望 code={case['expect_code']}，" \
        f"实际 code={resp['code']}，msg={resp['msg']}"

    # 断言 3：登录成功时，data 应该是字典（失败时是空字符串）
    if case["expect_code"] == 0:
        assert isinstance(resp["data"], dict), "登录成功但 data 字段结构异常"
