from django.apps import AppConfig

"""
修改默认的app显示名称

1. django在自动创建好app之后，在app下面会生成一个apps.py文件，该文件就是用于配置app显示名称的，
这是django的一种机制，xadmin也会认识这个配置，然后把他们显示到后台中

2. 还要在__init__.py中添加一个变量default_app_config，这是因为django新建app的时候，
并没有把__init__.py中加上引用，所以需要手动加上
"""


class UsersConfig(AppConfig):
    name = 'users'
    verbose_name = "用户信息"
