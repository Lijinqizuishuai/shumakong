# --coding:GBK --
from flask import render_template, redirect, request, jsonify, g, current_app

from . import profile_blue
from ... import constants, db
from ...models import News, Category
from ...utils.commons import user_login_data
from ...utils.image_storage import image_storage
from ...utils.response_code import RET


# 获取我的关注
@profile_blue.route('/user_follow')
@user_login_data
def user_follow():
    # 获取参数
    page = request.args.get("p", "1")
    # 参数类型转换
    try:
        page = int(page)
    except Exception as e:
        page = 1
    # 分类查询用户关注的作者
    try:
        paginate = g.user.followed.paginate(page, 4, False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取作者失败")
    # 获取分页的对象属性、总页数、当前页、当前页对象列表
    totalPage = paginate.pages
    currentPage = paginate.page
    items = paginate.items
    # 将对象列表转换成字典列表
    author_list = []
    for author in items:
        author_list.append(author.to_dict())
    # 拼接数据，渲染页面
    data = {
        "totalPage": totalPage,
        "currentPage": currentPage,
        "author_list": author_list
    }
    return render_template("news/user_follow.html", data=data)




@profile_blue.route('/news_list')
@user_login_data
def news_list():
    # 获取参数
    page = request.args.get("p", "1")
    # 参数类型转换
    try:
        page = int(page)
    except Exception as e:
        page = 1
    # 分类查询收藏的新闻
    try:
        paginate = News.query.filter(News.user_id==g.user.id).order_by(News.create_time.desc()).paginate(page,3,False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取新闻失败")
    # 获取分页的对象属性、总页数、当前页、当前页对象列表
    totalPage = paginate.pages
    currentPage = paginate.page
    items = paginate.items
    # 将对象列表转换成字典列表
    new_list = []
    for news in items:
        new_list.append(news.to_review_dict())
    # 拼接数据，渲染页面
    data = {
        "totalPage": totalPage,
        "currentPage": currentPage,
        "news_list": new_list
    }
    return render_template("news/user_news_list.html", data=data)




@profile_blue.route('/news_release',methods=['GET','POST'])
@user_login_data
def news_release():
    # 判断请求方式，如果是get请求，携带用户数据，渲染页面。
    if request.method == "GET":
        # 查询所有的分类数据
        try:
            categories=Category.query.all()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR,errmsg="获取分类失败")
        category_list=[]
        for category in categories:
            category_list.append(category.to_dict())
        return render_template("news/user_news_release.html",categories=category_list)
    # 如果是POST，获取参数
    title=request.form.get("title")
    category_id=request.form.get("category_id")
    digest=request.form.get("digest")
    index_image=request.files.get("index_image")
    content=request.form.get("content")
    print(title)
    print(category_id)
    print(digest)
    print(index_image)
    print(content)
    # 校验参数，为空校验
    if not all([title,category_id,digest,index_image,content]):
        return jsonify(errno=RET.PARAMERR,errmsg="参数不全")
    # 上传图片，判断是否上传成功
    try:
        # 读取图片为二进制数据，上传
        image_name=image_storage(index_image.read())
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR,errmsg="七牛云异常")
    if not image_name:
        return jsonify(errno=RET.NODATA,errmsg="图片上传失败")
    # 创建新闻对象，设置属性
    news=News()
    news.title=title
    news.source=g.user.nick_name
    news.digest=digest
    news.content=content
    news.index_image_url=constants.QINIU_DOMIN_PREFIX+image_name
    news.category_id=category_id
    news.user_id=g.user.id
    news.status=1 #表示审核中

    # 保存到数据
    try:
        db.session.add(news)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="新闻发布失败")

    return jsonify(errno=RET.OK,errmsg="新闻发布成功")



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