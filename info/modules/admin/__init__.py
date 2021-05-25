from flask import Blueprint, request, session, redirect

# 创建管理员蓝图对象
admin_blue=Blueprint("admin",__name__,url_prefix="/admin")
# 装饰视图函数
from . import views

# 使用请求钩子，拦截用户的请求，只有访问了admin_blue，所装饰的视图函数需要拦截
# 拦截的是访问了非登陆页面
# 拦截的是普通用户
@admin_blue.before_request
def before_request():
    # if request.url.endswith("/admin/login"):
    #     pass
    # else:
    #     if session.get("is_admin"):
    #         return redirect("/")
    if not request.url.endswith("/admin/login"):
        if not session.get("is_admin"):
            return redirect("/")
