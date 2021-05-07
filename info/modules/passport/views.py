import random
from datetime import datetime

from flask import request, current_app, make_response, jsonify, session
from info import models
from info.models import User
from ...utils.response_code import RET
from . import passport_blue
import re
from ... import redis_store, constants, db
from ...libs.yuntongxun import SmsSDK
from ...utils.captcha.captcha import captcha
import json

# 退出登录
# 请求路径：/passport/logout
# 请求方式：POST
# 请求参数：无
# 返回值：errno,errmsg
@passport_blue.route('/logout',methods=['POST'])
def logout():
    # 清除session信息
    session.pop("user_id",None)
    # 返回响应
    return jsonify(errno=RET.OK,errmsg="退出成功")

# 登录用户
# 请求方式：POST
# 请求路径：/passport/login
# 请求参数：mobile,password
# 返回值：errno,errmsg
@passport_blue.route('/login', methods=['POST'])
def login():
    # 获取参数
    mobile = request.json.get("mobile")
    password = request.json.get("password")
    # 校验参数，为空校验
    if not all([mobile, password]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不全")
    # 通过用户手机号，到数据库查询用户对象
    try:
        print("sss")
        user = User.query.filter(User.mobile == mobile).first()
        print("sss")
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取用户失败")
    # 判断用户是否存在
    if not user:
        return jsonify(errno=RET.NODATA, errmsg="用户不存在")
    # 校验密码是否正确
    if not user.check_passowrd(password):
        return jsonify(errno=RET.DATAERR, errmsg="密码错误")
    # 将用户的登录信息保存在session中
    session["user_id"] = user.id
    # 记录用户最后一次的登陆时间
    user.last_login = datetime.now()
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
    # 返回响应
    return jsonify(errno=RET.OK, errmsg="登陆成功")


# 注册用户
# 请求方式：POST
# 请求路径：/passport/register
# 请求参数：mobile,sms_code,password
# 返回值：errno,errmsg
@passport_blue.route('/register', methods=['POST'])
def register():
    # 获取参数
    json_date = request.data
    dict_date = json.loads(json_date)
    mobile = dict_date.get("mobile")
    sms_code = dict_date.get("sms_code")
    password = dict_date.get("password")
    # 校验参数，为空校验
    if not all([mobile, sms_code, password]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不全")
    # 手机号作为key取出redis中的短信验证码
    try:
        redis_sms_code = redis_store.get("sms_code:%s" % mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="短信验证码取出失败")
    # 判断短信验证码是否过期
    if not redis_sms_code:
        return jsonify(errno=RET.NODATA, errmsg="短信验证码过期")
    # 判断短信验证码是否正确
    if redis_sms_code != sms_code:
        return jsonify(errno=RET.DATAERR, errmsg="短信验证码填写错误")
    # 删除短信验证码
    try:
        redis_store.delete("sms_code:%s" % mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="短信验证码删除失败")
    # 创建用户对象
    user = User()
    # 设置用户对象属性
    user.nick_name = mobile
    user.password = password
    user.mobile = mobile
    user.signature = "该用户很懒，什么都没写"

    # 保存用户到数据库
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="用户注册失败")
    # 返回响应
    return jsonify(errno=RET.OK, errmsg="注册成功")


# 获取短信验证码
# 请求路径：/passport/sms_code
# 请求方式：POST
# 请求参数：mobile，image_code,image_code_id
# 返回值：errno，errmsg
@passport_blue.route('/sms_code', methods=['POST'])
def sms_code():
    #     获取参数
    dict_data = request.json
    mobile = dict_data.get("mobile")
    image_code = dict_data.get("image_code")
    image_code_id = dict_data.get("image_code_id")
    # 参数为空校验
    if not all([mobile, image_code, image_code_id]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不全")
    # 校验参数、手机格式
    if not re.match("1[3-9]\d{9}", mobile):
        return jsonify(errno=RET.DATAERR, errmsg="手机号格式不匹配")
    # 从redis中取出图片验证码
    try:
        redis_image_code = redis_store.get("image_code:%s" % image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="操作redis失败")

    # 判断图片验证码是否过期
    if not redis_image_code:
        return jsonify(errno=RET.NODATA, errmsg="图片验证码已经过期")
    # 和传递的图片验证码比较
    if image_code.upper() != redis_image_code.upper():
        return jsonify(errno=10000, errmsg="图片验证码填错了")
    # 删除redis中的图片验证码
    try:
        redis_store.delete("image_code:%s" % image_code_id)
    except Exception as e:
        return jsonify(errno=RET.DBERR, errmsg="删除redis图片验证码失败")
    sms_code = "%06d" % random.randint(0, 999999)
    """
    accId = '8a216da878005a8001788757c21632b5'
    accToken = '2ed3c4b28e734a4186d923e9f8d80727'
    appId = '8a216da878005a8001788757c3f432bb'
    sms = SmsSDK(accId,accToken,appId)
    
    result = sms.sendMessage('1','17721235356',(sms_code, constants.SMS_CODE_REDIS_EXPIRES/60))
    if result == -1:
        return jsonify(errno=30000, errmsg="短信发送失败")
    """
    print(sms_code)
    # 将短信保存到redis
    try:
        redis_store.set("sms_code:%s" % mobile, sms_code, constants.SMS_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="短信验证码保存到redis失败")

    # 返回发送的状态
    return jsonify(errno=RET.OK, errmsg="短信发送成功")


# 功能：获取图片验证码
# 请求路径：/passport/image_code
# 请求方式：get
# 携带参数：cur_id,pre_id
# 返回值：图片验证码

@passport_blue.route('/image_code')
def image_code():
    # 获取前端传递的参数
    cur_id = request.args.get("cur_id")
    pre_id = request.args.get("pre_id")

    # 调用generate_captcha获取图片验证码编号、验证码值、图片（二进制）
    name, text, image_data = captcha.generate_captcha()

    # 将图片验证码的值保存redis
    try:
        # 参数1：key，参数2：value，参数3：有效期
        redis_store.set("image_code:%s" % cur_id, text, constants.IMAGE_CODE_REDIS_EXPIRES)

        # 判断是否有上一次的图片验证码
        if pre_id:
            redis_store.delete("image_code:%s" % pre_id)
    except Exception as e:
        current_app.logger.error(e)
        return "图片验证码操作失败"
    # 返回图片
    response = make_response(image_data)
    response.headers["Content-Type"] = "image/png"
    return response
