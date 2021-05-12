# �Զ��������ʵ���������ŵ���ɫ����
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


# �����½װ��������װ�û��ĵ�¼����
def user_login_data(view_func):
    @wraps(view_func)
    def wrapper(*args,**kwargs):
        # ��session��ȡ���û���user_id
        user_id = session.get("user_id")
        # ͨ��user_idȡ���û�����
        user = None
        if user_id:
            try:
                from info.models import User
                user = User.query.get(user_id)
            except Exception as e:
                current_app.logger.error(e)
        # ��user���ݷ�װ��g����
        g.user=user
        return view_func(*args,**kwargs)
    return wrapper