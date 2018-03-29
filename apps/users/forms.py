__author__ = 'wqq'
__date__ = '2018/3/29 11:06'
from django import forms

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
