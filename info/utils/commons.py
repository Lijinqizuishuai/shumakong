# 自定义过滤器实现热门新闻的颜色过滤
from functools import wraps

from flask import session, current_app, g


def hot_news_filter(index):
    if index ==1:
        return "first"
    elif index==2:
        return "second"
    elif index ==3:
        return "third"
    else:
        return ""


# 定义登陆装饰器，封装用户的登录数据
def user_login_data(view_func):
    @wraps(view_func)
    def wrapper(*args,**kwargs):
        # 从session中取出用户的user_id
        user_id = session.get("user_id")
        # 通过user_id取出用户对象
        user = None
        if user_id:
            try:
                from info.models import User
                user = User.query.get(user_id)
            except Exception as e:
                current_app.logger.error(e)
        # 将user数据封装到g对象
        g.user=user
        return view_func(*args,**kwargs)
    return wrapper