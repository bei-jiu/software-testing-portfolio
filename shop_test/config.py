# 被测系统地址（ShopXO 商城测试环境）
HOST = "http://shop-xo.hctestedu.com/"

# 登录接口（ShopXO 前端用户登录）
LOGIN_URL = HOST + "index.php?s=/index/user/login.html"

# ShopXO 的 AJAX 接口必须带这个请求头才会返回 JSON，
# 否则会返回一段 HTML 错误页面。前端登录表单就是带这个头发请求的。
AJAX_HEADERS = {
    "X-Requested-With": "XMLHttpRequest",
}
