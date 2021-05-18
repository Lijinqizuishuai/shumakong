# --coding:GBK --
from flask import render_template, redirect, request, jsonify, g, current_app

from . import profile_blue
from ... import constants
from ...models import News
from ...utils.commons import user_login_data
from ...utils.image_storage import image_storage
from ...utils.response_code import RET

@profile_blue.route('/collection')
@user_login_data
def collection():
    # ��ȡ����
    page=request.args.get("p","1")
    # ��������ת��
    try:
        page=int(page)
    except Exception as e:
        page=1
    # �����ѯ�ղص�����
    try:
        paginate=g.user.collection_news.order_by(News.create_time.desc()).paginate(page,10,False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="��ȡ����ʧ��")
    # ��ȡ��ҳ�Ķ������ԡ���ҳ������ǰҳ����ǰҳ�����б�
    totalPage=paginate.pages
    currentPage=paginate.page
    items=paginate.items
    # �������б�ת�����ֵ��б�
    new_list=[]
    for news in items:
        new_list.append(news.to_dict())
    # ƴ�����ݣ���Ⱦҳ��
    data={
        "totalPage":totalPage,
        "currentPage":currentPage,
        "news_list":new_list
    }
    return render_template("news/user_collection.html",data=data)

@profile_blue.route('/pass_info', methods=['GET', 'POST'])
@user_login_data
def pass_info():
    # �ж�����ʽ�������get����Я���û����ݣ���Ⱦҳ�档
    if request.method == "GET":
        # Я���û����ݣ���Ⱦҳ��
        return render_template("news/user_pass_info.html", user_info=g.user.to_dict())
    # �����post���󣬻�ȡ����
    old_password = request.json.get("old_password")
    new_password = request.json.get("new_password")
    # У�������Ϊ��У��
    if not all([old_password,new_password]):
        return jsonify(errno=RET.PARAMERR,errmsg="������ȫ")
    # �ж��������Ƿ���ȷ
    if not g.user.check_passowrd(old_password):
        return jsonify(errno=RET.DATAERR,errmsg="���������")
    # ����������
    g.user.password=new_password
    # ������Ӧ
    return jsonify(errno=RET.OK,errmsg="�޸ĳɹ�")


# ��ȡ/���ã��û�ͷ���ϴ�
@profile_blue.route('/pic_info',methods=['GET','POST'])
@user_login_data
def pic_info():
    # �ж�����ʽ�������get����Я���û����ݣ���Ⱦҳ�档
    if request.method =="GET":
        # Я���û����ݣ���Ⱦҳ��
        return render_template("news/user_pic_info.html",user_info=g.user.to_dict())
    # �����post����
    # ��ȡ����
    avatar=request.files.get("avatar")
    # У�����Ϊ��У��
    if not avatar:
        return jsonify(errno=RET.PARAMERR,errmsg="ͼƬ����Ϊ��")
    # �ϴ�ͼ���ж�ͼƬ�Ƿ��ϴ��ɹ�
    try:
        image_name=image_storage(avatar.read())
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR,errmsg="��ţ���쳣")
    if not image_name:
        return jsonify(errno=RET.NODATA,errmsg="ͼƬ�ϴ�ʧ��")
    # ��ͼƬ���õ��û�����
    g.user.avatar_url=image_name
    data={
        "avatar_url":constants.QINIU_DOMIN_PREFIX+image_name
    }
    # ������Ӧ
    return jsonify(errno=RET.OK,errmsg="�ϴ��ɹ�",data=data)


@profile_blue.route('/base_info', methods=['GET', 'POST'])
@user_login_data
def base_info():
    # �ж�����ʽ�������get����
    if request.method =="GET":
        # Я���û����ݣ���Ⱦҳ��
        print(1)
        return render_template("news/user_base_info.html",user_info=g.user.to_dict())
    # �����post����
    # ��ȡ����
    nick_name=request.json.get("nick_name")
    signature=request.json.get("signature")
    gender=request.json.get("gender")
    # ����У�飬Ϊ��У��
    print(nick_name)
    print(signature)
    print(gender)


    if not all([nick_name,signature,gender]):
        return jsonify(errno=RET.PARAMERR,errmsg="������ȫ")
    if not gender in ["MAN","WOMAN"]:
        return jsonify(errno=RET.DATAERR,errmsg="�Ա��쳣")
    # �޸��û�������
    g.user.signature=signature
    g.user.nick_name=nick_name
    g.user.gender=gender

    # ������Ӧ
    return jsonify(errno=RET.OK,errmag="�޸ĳɹ�")







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