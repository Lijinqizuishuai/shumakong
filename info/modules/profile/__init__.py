from flask import Blueprint

# ������ͼ����
profile_blue= Blueprint("profile",__name__,url_prefix="/user")

# װ����ͼ����
from . import views

