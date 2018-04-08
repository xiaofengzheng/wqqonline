__author__ = 'wqq'
__date__ = '2018/3/28 9:38'

"""
django admin自动生成了一个admin.py，xadmin和django admin用法相似
但是我们要新建一个adminx.py文件，因为xadmin会自动搜寻每个app下的adminx.py文件，然后根据该文件来注册model
"""
import xadmin
from xadmin import views

from .models import EmailVerifyRecord, Banner


class BaseSetting(object):
    # xadmin默认是把主题功能取消掉的
    enable_themes = True
    use_bootswatch = True


class GlobalSetting(object):
    """
    后台的顶部和底部信息还有菜单折叠
    """
    site_title = "wqq后台管理系统"
    site_footer = "wqq在线网"
    menu_style = "accordion"


class EmailVerifyRecordAdmin(object):
    """
    在这里不再像admin那样继承admin.ModelAdmin，而是继承最底层的类object
    """

    # 在列表中显示的字段，也可以写成元组形式
    list_display = ['email', 'code', 'send_type', 'send_time']
    # 在做搜索的时候，后台是在哪些字段中进行搜索的，时间搜索是不好走的，不按send_time进行搜索
    search_fields = ['email', 'code', 'send_type']
    # 生成过滤器
    list_filter = ['email', 'code', 'send_type', 'send_time']
    # model_icon = 'fa fa-area-char'  # 定制图标


class BannerAdmin(object):
    list_display = ['title', 'image', 'url', 'index', 'add_time']
    search_fields = ['title', 'image', 'url', 'index']
    list_filter = ['title', 'image', 'url', 'index', 'add_time']


xadmin.site.register(EmailVerifyRecord, EmailVerifyRecordAdmin)
xadmin.site.register(Banner, BannerAdmin)
xadmin.site.register(views.BaseAdminView, BaseSetting)
xadmin.site.register(views.CommAdminView, GlobalSetting)