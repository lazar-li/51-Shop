import os


class Config:
    FLASK_APP = "manage.py"
    SECRET_KEY = 'mrsoft'
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    @staticmethod
    def init_app(app):
        '''初始化配置文件'''
        pass


# the config for development
class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:542858zry@39.98.192.225:3306/shop'
    DEBUG = True

class SocialConfig(Config):
    # 第三方登录，里面的值是你的开放平台对应的值
    SOCIAL_AUTH_WEIBO_KEY = '9f6847c4f4a593e31af99d58269c8af2'
    SOCIAL_AUTH_WEIBO_SECRET = '3946853933'

    SOCIAL_AUTH_QQ_KEY = '9f6847c4f4a593e31af99d58269c8af2'
    SOCIAL_AUTH_QQ_SECRET = '3946853933'

    SOCIAL_AUTH_WEIXIN_KEY = '9f6847c4f4a593e31af99d58269c8af2'
    SOCIAL_AUTH_WEIXIN_SECRET = '3946853933'
    # 登录成功后跳转到首页
    SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/index/'
# define the config
config = {
    'default': DevelopmentConfig
}
