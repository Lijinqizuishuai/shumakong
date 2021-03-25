from . import index_blue

@index_blue.route('/',methods=["GET","POST"])
def hello_world():
    # redis_store.set("name","laowang")
    # print(redis_store.get("name"))
    #
    # session["name"] = "zhangsan"
    # print(session.get("name"))
    return "helloworld"
