__author__ = 'wqq'
__date__ = '2018/4/4 18:33'

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


class LoginRequiredMixin(object):
    """
    login_required：判断用户是否登陆，如果用户处于未登录状态，就自动跳到login_url
    """
    @method_decorator(login_required(login_url='/login/'))
    def dispatch(self, request, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(request, *args, **kwargs)

