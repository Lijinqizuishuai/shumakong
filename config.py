from datetime import timedelta

from redis import StrictRedis

# 设置配置信息（基类配置信息）
class Config(object):
    DEBUG = True
    SECRET_KEY = "fsfssfs"

    SQLALCHEMY_DATABASE_URI = "mysql://root:mysql@127.0.0.1/info36"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379

    SESSION_TYPE = "redis"
    SESSION_REDIS = StrictRedis(host = REDIS_HOST,port= REDIS_PORT)
    SESSION_USE_SIGNER = True
    PERMANENT_SESSION_LIFETIME = timedelta(days=5) # 设置session有效期
# 开发环境配置信息
class DevelopConfig(Config):
    pass

# 生产（线上）环境配置信息
class ProductConfig(Config):
    DEBUG = False

# 测试环境配置信息
class TestConfig(Config):
    pass

# 提供一个统一的访问入口
config_dict = {
    "develop":DevelopConfig,
    "product":ProductConfig,
    "test":TestConfig
}