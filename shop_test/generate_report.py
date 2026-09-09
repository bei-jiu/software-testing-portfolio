"""一键生成中文版 Allure 报告。

用法（在 shop_test 目录下）：
    1. 先运行测试，生成 allure 结果：  python -m pytest
    2. 再运行本脚本：                 python generate_report.py

本脚本会：
    - 调用 allure 命令行工具生成 HTML 报告
    - 把报告默认语言改成中文（Allure 2.46 自带中文翻译，只需改 <html lang="zh">）
"""
import subprocess
from pathlib import Path

# Allure 命令行工具的完整路径（改成你自己的路径）
ALLURE = r"C:\Users\1\allure-2.46.1\bin\allure.bat"

RESULT_DIR = "allure-results"
REPORT_DIR = "allure-report"
INDEX_FILE = Path(REPORT_DIR) / "index.html"


def generate():
    # 1. 生成报告
    subprocess.run(
        [ALLURE, "generate", RESULT_DIR, "-o", REPORT_DIR, "--clean"],
        check=True,
    )

    # 2. 汉化：把 <html lang="en"> 改成 <html lang="zh">
    html = INDEX_FILE.read_text(encoding="utf-8")
    html = html.replace('<html dir="ltr" lang="en">', '<html dir="ltr" lang="zh">')
    INDEX_FILE.write_text(html, encoding="utf-8")

    print("中文版报告已生成：allure-report/index.html")
    print("用浏览器打开即可（推荐：allure open allure-report）")


if __name__ == "__main__":
    generate()
