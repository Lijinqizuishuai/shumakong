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
    # 获取参数
    page=request.args.get("p","1")
    # 参数类型转换
    try:
        page=int(page)
    except Exception as e:
        page=1
    # 分类查询收藏的新闻
    try:
        paginate=g.user.collection_news.order_by(News.create_time.desc()).paginate(page,10,False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="获取新闻失败")
    # 获取分页的对象属性、总页数、当前页、当前页对象列表
    totalPage=paginate.pages
    currentPage=paginate.page
    items=paginate.items
    # 将对象列表转换成字典列表
    new_list=[]
    for news in items:
        new_list.append(news.to_dict())
    # 拼接数据，渲染页面
    data={
        "totalPage":totalPage,
        "currentPage":currentPage,
        "news_list":new_list
    }
    return render_template("news/user_collection.html",data=data)

@profile_blue.route('/pass_info', methods=['GET', 'POST'])
@user_login_data
def pass_info():
    # 判断请求方式，如果是get请求，携带用户数据，渲染页面。
    if request.method == "GET":
        # 携带用户数据，渲染页面
        return render_template("news/user_pass_info.html", user_info=g.user.to_dict())
    # 如果是post请求，获取参数
    old_password = request.json.get("old_password")
    new_password = request.json.get("new_password")
    # 校验参数，为空校验
    if not all([old_password,new_password]):
        return jsonify(errno=RET.PARAMERR,errmsg="参数不全")
    # 判断老密码是否正确
    if not g.user.check_passowrd(old_password):
        return jsonify(errno=RET.DATAERR,errmsg="老密码错误")
    # 设置新密码
    g.user.password=new_password
    # 返回响应
    return jsonify(errno=RET.OK,errmsg="修改成功")


# 获取/设置，用户头像上传
@profile_blue.route('/pic_info',methods=['GET','POST'])
@user_login_data
def pic_info():
    # 判断请求方式，如果是get请求，携带用户数据，渲染页面。
    if request.method =="GET":
        # 携带用户数据，渲染页面
        return render_template("news/user_pic_info.html",user_info=g.user.to_dict())
    # 如果是post请求
    # 获取参数
    avatar=request.files.get("avatar")
    # 校验参数为空校验
    if not avatar:
        return jsonify(errno=RET.PARAMERR,errmsg="图片不能为空")
    # 上传图像，判断图片是否上传成功
    try:
        image_name=image_storage(avatar.read())
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR,errmsg="七牛云异常")
    if not image_name:
        return jsonify(errno=RET.NODATA,errmsg="图片上传失败")
    # 将图片设置到用户对象
    g.user.avatar_url=image_name
    data={
        "avatar_url":constants.QINIU_DOMIN_PREFIX+image_name
    }
    # 返回响应
    return jsonify(errno=RET.OK,errmsg="上传成功",data=data)


@profile_blue.route('/base_info', methods=['GET', 'POST'])
@user_login_data
def base_info():
    # 判断请求方式，如果是get请求
    if request.method =="GET":
        # 携带用户数据，渲染页面
        print(1)
        return render_template("news/user_base_info.html",user_info=g.user.to_dict())
    # 如果是post请求
    # 获取参数
    nick_name=request.json.get("nick_name")
    signature=request.json.get("signature")
    gender=request.json.get("gender")
    # 参数校验，为空校验
    print(nick_name)
    print(signature)
    print(gender)


    if not all([nick_name,signature,gender]):
        return jsonify(errno=RET.PARAMERR,errmsg="参数不全")
    if not gender in ["MAN","WOMAN"]:
        return jsonify(errno=RET.DATAERR,errmsg="性别异常")
    # 修改用户的数据
    g.user.signature=signature
    g.user.nick_name=nick_name
    g.user.gender=gender

    # 返回响应
    return jsonify(errno=RET.OK,errmag="修改成功")







@profile_blue.route('/info')
@user_login_data
def user_index():

    # 判断用户是否登录
    if not g.user:
        return redirect("/")
    # 携带数据渲染页面
    data={
        "user_info":g.user.to_dict()
    }
    return render_template("news/user.html",data=data)