# -*- coding: utf-8 -*-
from flask import current_app, jsonify, render_template, session, g, request

from . import news_blue

# 请求路径：/news/<int:news_id>
# 请求方式：GET
# 请求参数：news_id
# 返回值:detail.html页面，用户data字典数据
from ... import db
from ...models import News, User, Comment, CommentLike
from ...utils.commons import user_login_data
from ...utils.response_code import RET

@news_blue.route('/comment_like',methods=['POST'])
@user_login_data
def comment_like():
    # 判断用户是否登录
    if not g.user:
        return jsonify(error=RET.NODATA,errmsg="用户未登录")
    # 获取参数
    comment_id = request.json.get("comment_id")
    action = request.json.get("action")
    # 参数校验，为空校验
    if not all([comment_id,action]):
        return jsonify(errno=RET.PARAMERR,errmsg="参数不全")
    # 操作类型进行校验
    if not action in ["add","remove"]:
        return jsonify(errno=RET.DATAERR,errmsg="操作类型有误")
    # 通过评论编号查询评论对象，并判断是否存在
    try:
        comment=Comment.query.get(comment_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="获取评论失败")
    if not comment:
        return jsonify(errno=RET.NODATA,errmsg="评论不存在")
    # 根据操作类型点赞取消点赞
    try:
        if action=="add":
            comment_like =CommentLike.query.filter(CommentLike.user_id==g.user.id,CommentLike.comment_id==comment_id).first()
            if not comment_like:
                comment_like=CommentLike()
                comment_like.user_id=g.user.id
                comment_like.comment_id=comment_id
                db.session.add(comment_like)
                comment.like_count+=1
                print(comment_like)
                db.session.commit()
        else:
            comment_like = CommentLike.query.filter(CommentLike.user_id == g.user.id,CommentLike.comment_id == comment_id).first()
            if comment_like:
                db.session.delete(comment_like)
                if comment.like_count > 0:
                    comment.like_count -= 1
                db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="操作失败")
    # 返回响应
    return jsonify(errno=RET.OK,errmsg="操作成功")

@news_blue.route('/news_comment',methods=['POST'])
@user_login_data
def news_comment():
    # 判断用户是否登录
    if not g.user:
        return jsonify(error=RET.NODATA,errmsg="用户未登录")
    # 获取请求参数
    news_id = request.json.get("news_id")
    content=request.json.get("comment")
    parent_id=request.json.get("parent_id")
    # 校验参数，为空校验
    if parent_id:
        news_id= Comment.query.get(parent_id).news_id
    if not all([news_id,content]):
        return jsonify(errno=RET.PARAMERR,errmsg="参数不全")

    # 根据新闻编号取出新闻对象，判断新闻是否存在
    try:
        news=News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="获取新闻失败")
    if not news:
        return  jsonify(errno=RET.NODATA,errmsg="新闻不存在")
    # 创建评论对象，设置属性
    comment=Comment()
    comment.user_id=g.user.id
    comment.news_id=news_id
    comment.content=content
    if parent_id:
        comment.parent_id=parent_id
    # 保存评论对象到数据库
    try:
        db.session.add(comment)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="评论失败")
    # 返回响应，携带评论的数据

    return jsonify(errno=RET.OK,errmsg="评论成功",data=comment.to_dict())
@news_blue.route('/news_collect',methods=['POST'])
@user_login_data
def news_collect():
    # 判断用户是否登陆了
    if not g.user:
        return jsonify(error=RET.NODATA,errmsg="用户未登录")
    # 获取参数
    news_id = request.json.get("news_id")
    action = request.json.get("action")
    # 参数校验，为空校验
    if not all([news_id,action]):
        return jsonify(error=RET.PARAMERR,errmsg="参数不全")
    # 操作类型校验
    if not action in ["collect","cancel_collect"]:
        return jsonify(error=RET.DATAERR,errmsg="操作类型有误")
    # 根据新闻的编号取出新闻对象
    try:
        news=News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error=RET.DBERR,errmsg="新闻获取失败")
    # 判断新闻对象是否存在
    if not news:
        return jsonify(errno=RET.NODATA,errmsg="新闻不存在")
    # 根据操作类型，进行收藏&取消收藏操作
    if action=="collect":
        if not news in g.user.collection_news:
            g.user.collection_news.append(news)
    else:
        if news in g.user.collection_news:
            g.user.collection_news.remove(news)
    # 返回响应
    return jsonify(errno=RET.OK,errmsg="操作成功")

@news_blue.route('/<int:news_id>')
@user_login_data
def news_detail(news_id):

    # # 从session中取出用户的user_id
    # user_id =session.get("user_id")
    # # 通过user_id取出用户对象
    # user=None
    # if user_id:
    #     try:
    #         user = User.query.get(user_id)
    #     except Exception as e:
    #         current_app.logger.error(e)

    # 根据新闻编号查询新闻对象
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="获取新闻失败")

    # 如果新闻不存在，直接排除异常
    if not news:
        abort(404)


    # 获取前6条热门新闻
    try:
        click_news= News.query.order_by(News.clicks.desc()).limit(6).all()
    except Exception as e:
        current_app.logger.error(e)

    # 将热门新闻的对象列表转成字典列表
    click_news_list= []
    for item_news in click_news:
        click_news_list.append(item_news.to_dict())

    # 判断用户是否收藏过该新闻
    is_collected = False
    # 用户需要登录，并且该新闻在用户收藏过的新闻列表中
    if g.user:
        if news in g.user.collection_news:
            is_collected = True

    # 查询数据库中，该新闻的所有评论内容
    try:
        comments=Comment.query.filter(Comment.news_id==news_id).order_by(Comment.create_time.desc()).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="获取评论失败")

    # 用户点赞过的评论编号
    try:
        commentlikes=[]
        if g.user:
            commentlikes=CommentLike.query.filter(CommentLike.user_id ==g.user.id).all()
        mylike_comment_ids=[]
        for commentLike in commentlikes:
            mylike_comment_ids.append(commentLike.comment_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="获取点赞失败")
    # 将评论的对象列表，转成字典列表
    comments_list = []
    for comment in comments:
        comm_dict=comment.to_dict()
        comm_dict["is_like"]=False
        if g.user and comment.id in mylike_comment_ids:
            comm_dict["is_like"] =True

        comments_list.append(comm_dict)
    # 携带数据，渲染页面
    data={
        "news_info":news.to_dict(),
        "user_info":g.user.to_dict() if g.user else "",
        "news":click_news_list,
        "is_collected":is_collected,
        "comments":comments_list
    }


    return render_template("news/detail.html",data=data)