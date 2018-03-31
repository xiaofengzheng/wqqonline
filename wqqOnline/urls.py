"""wqqOnline URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Import the include() function: from django.conf.urls import url, include
    3. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import url, include
# from django.contrib import admin
import xadmin
from django.views.generic import TemplateView
from django.views.static import serve  # 处理静态文件

# from users.views import user_login
from users.views import LoginView, RegisterView, ActiveUserView, ForgetPwdView, ResetView, ModifyPwdView
from organization.views import OrgView
from wqqOnline.settings import MEDIA_ROOT

"""
TemplateView是专门用于处理静态文件的
TemplateView.as_view方法会把template自动转换成一个view函数
"""

urlpatterns = [
    url(r'^xadmin/', xadmin.site.urls),
    url(r'^$', TemplateView.as_view(template_name='index.html'), name='index'),
    # template_name='index.html'写的并不是路径，因为django能自动识别出templates就是存放HTML的路径（settings.py中有相关设置）
    # url('login/$', user_login, name='login')
    url(r'^login/$', LoginView.as_view(), name='login'),
    # LoginView.as_view()把LoginView转换成一个as_view，这个as_view会返回一个函数的句柄，
    # 这个是因为调用方法，所以需要后面有括号，该方法返回一个函数的句柄
    url(r'^register/$', RegisterView.as_view(), name='register'),
    url(r'^captcha/', include('captcha.urls')),
    url(r'^active/(?P<active_code>.*)/$', ActiveUserView.as_view(), name='user_active'),
    url(r'^forget/$', ForgetPwdView.as_view(), name='forget_pwd'),
    url(r'^reset/(?P<active_code>.*)/$', ResetView.as_view(), name='reset_pwd'),
    url(r'^modify_pwd/$', ModifyPwdView.as_view(), name='modify_pwd'),

    # 课程机构首页
    url(r'^org_list/$', OrgView.as_view(), name='org_list'),

    # 配置上传文件的访问处理函数
    url(r'^media/(?P<path>.*)/$', serve, {'document_root': MEDIA_ROOT})

]
