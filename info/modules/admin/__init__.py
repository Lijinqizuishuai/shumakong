from flask import Blueprint, request, session, redirect

# ��������Ա��ͼ����
admin_blue=Blueprint("admin",__name__,url_prefix="/admin")
# װ����ͼ����
from . import views

# ʹ�������ӣ������û�������ֻ�з�����admin_blue����װ�ε���ͼ������Ҫ����
# ���ص��Ƿ����˷ǵ�½ҳ��
# ���ص�����ͨ�û�
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
