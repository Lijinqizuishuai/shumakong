from flask import  Blueprint

# ������ͼ����
news_blue = Blueprint("news",__name__,url_prefix="/news")

# ������ͼ����װ����ͼ����
from . import views