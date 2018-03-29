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
from django.conf.urls import url
# from django.contrib import admin
import xadmin
from django.views.generic import TemplateView

# from users.views import user_login
from users.views import LoginView, RegisterView

"""
TemplateView是专门用于处理静态文件的
TemplateView.as_view方法会把template自动转换成一个view函数
"""

urlpatterns = [
    url(r'^xadmin/', xadmin.site.urls),
    url('^$', TemplateView.as_view(template_name='index.html'), name='index'),
    # template_name='index.html'写的并不是路径，因为django能自动识别出templates就是存放HTML的路径（settings.py中有相关设置）
    # url('login/$', user_login, name='login')
    url('login/$', LoginView.as_view(), name='login'),
    # LoginView.as_view()把LoginView转换成一个as_view，这个as_view会返回一个函数的句柄，
    # 这个是因为调用方法，所以需要后面有括号，该方法返回一个函数的句柄
    url('register/$', RegisterView.as_view(), name='register')

]
