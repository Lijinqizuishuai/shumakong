# -*- coding: utf-8 -*-
from flask import current_app, jsonify, render_template, session, g

from . import news_blue

# 请求路径：/news/<int:news_id>
# 请求方式：GET
# 请求参数：news_id
# 返回值:detail.html页面，用户data字典数据
from ...models import News, User
from ...utils.commons import user_login_data
from ...utils.response_code import RET


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

    # 携带数据，渲染页面
    data={
        "news_info":news.to_dict(),
        "user_info":g.user.to_dict() if g.user else "",
        "news":click_news_list,
        "is_collected":is_collected
    }


    return render_template("news/detail.html",data=data)