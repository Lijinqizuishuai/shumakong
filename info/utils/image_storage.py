# -*- coding: utf-8 -*-
# flake8: noqa
from qiniu import Auth, put_file, etag,put_data
import qiniu.config
#需要填写你的 Access Key 和 Secret Key
access_key = 'ZXMvWq52rcQHkUPqJbaxoqEz5b-FkRwVAIZWJgEK'
secret_key = 'cydlum3Y9V4_bMn2LkGvgWIJ1yENsoIl2uABvTRZ'


def image_storage(image_data):
    #构建鉴权对象


    q = Auth(access_key, secret_key)
    #要上传的空间
    bucket_name = 'shumakong'
    #上传后保存的文件名，如果不指定，那么由七牛云自己维护
    # key = 'haha.png'
    key=None
    #生成上传 Token，可以
    # 指定过期时间等
    token = q.upload_token(bucket_name, key, 3600)
    #要上传文件的本地路径
    # localfile = 'C:/Users/大梦想家/Desktop/1.png'


    # ret, info = put_file(token, key, localfile)
    ret, info = put_data(token, key, image_data)
    # 处理上传结果,返回图片名称
    if info.status_code==200:
        return ret.get("key")
    else:
        return None
if __name__ == '__main__':
    with open('C:/Users/大梦想家/Desktop/1.png','rb') as f:
            image_storage(f.read())