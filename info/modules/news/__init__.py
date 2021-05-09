from flask import  Blueprint

# 创建蓝图对象
news_blue = Blueprint("news",__name__,url_prefix="/news")

# 创建蓝图对象，装饰视图函数
from . import views