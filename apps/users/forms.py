__author__ = 'wqq'
__date__ = '2018/3/29 11:06'
from django import forms
from captcha.fields import CaptchaField

from .models import UserProfile

"""
把用户提交过来的表单做一部分预处理，比如说判断这个字段是否必须存在，不存在就说这个字段必须得填，最大长度是多少，
这种判断实际上是很复杂的，如果面面俱到的话，就会发现大量的判断逻辑chong刺着post函数。
如果有forms的话，就可以通过Form来验证这些参数是否正确，比如说最大长度、是否为空，Form都会自动为我们做，
在判断这些所有都通过后再写我们的逻辑，就减少了很多代码
"""


class LoginForm(forms.Form):
    username = forms.CharField(required=True)
    # required=True在做验证的时候，如果这个字段为空就会报错
    password = forms.CharField(required=True, min_length=5)
    # min_length=5在做验证的时候，如果该字段长度<5，根本就不去数据库里查，forms直接就验证失败


class RegisterForm(forms.Form):
    """
    这个From实际上是对我们注册表单的一个验证
    """
    email = forms.EmailField(required=True)
    # 只需要用这个forms.EmailField，在前端传过来email字段时，就必须符合email的一个正则表达式，
    # 这个实际上是forms.EmailField已经在后台替我们验证了
    # 这个Form实际上我们在把它生成字符串的时候，它是会生成一段html代码的，
    # 比如说EmailField、CaptchaField实际上会生成一个input框，不同的Field会生成不同的html代码
    password = forms.CharField(required=True, min_length=5)
    captcha = CaptchaField(error_messages={'invalid':"验证码错误"})
    # CaptchaField默认的报错信息是：invalid captcha，可以通过传入一个参数error_messages定制错误信息
    # CaptchaField在检查的时候，会报一个invalid异常，所以error_messages里面的键必须和这个异常名称一样


class ForgetForm(forms.Form):
    email = forms.EmailField(required=True)
    captcha = CaptchaField(error_messages={'invalid': "验证码错误"})


class ModifyPwdForm(forms.Form):
    password1 = forms.CharField(required=True, min_length=5)
    password2 = forms.CharField(required=True, min_length=5)


class UploadImageForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['image']


class UploadInfoForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['nick_name', 'gender', 'birday', 'address', 'mobile']