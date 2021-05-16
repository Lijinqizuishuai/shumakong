from flask import render_template, redirect

from . import profile_blue
from ...utils.commons import user_login_data


@profile_blue.route('/info')
@user_login_data
def user_index():

    # �ж��û��Ƿ��¼
    if not g.user:
        return redirect("/")
    # Я��������Ⱦҳ��
    data={
        "user_info":g.user.to_dict()
    }
    return render_template("news/user.html",data=data)