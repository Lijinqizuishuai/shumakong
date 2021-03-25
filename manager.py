

from info import create_app

app = create_app("develop")

@app.route('/',methods=["GET","POST"])
def hello_world():
    # redis_store.set("name","laowang")
    # print(redis_store.get("name"))
    #
    # session["name"] = "zhangsan"
    # print(session.get("name"))
    return "helloworld"

if __name__ == '__main__':

    app.run()