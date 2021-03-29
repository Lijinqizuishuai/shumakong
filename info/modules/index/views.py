from . import index_blue
from ... import redis_store
import logging

@index_blue.route('/',methods=["GET","POST"])
def hello_world():
    redis_store.set("name","laowang")
    print(redis_store.get("name"))
    #
    # session["name"] = "zhangsan"
    # print(session.get("name"))

    #使用日志记录方法loggin进行输出可控
    logging.debug("输出调试信息")
    logging.info("输出详细信息")
    logging.warning("输出警告信息")
    logging.error("输出错误信息")


    return "helloworld"
