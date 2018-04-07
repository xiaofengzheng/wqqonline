__author__ = 'wqq'
__date__ = '2018/3/31 18:43'
import re
from django import forms

from operation.models import UserAsk


# class UserAskForm(forms.Form):
#     """
#     这是之前的表单验证方法，本节将将另一个更强大的表单验证方法(ModelForm)
#     """
#     name = forms.CharField(required=True, min_length=2, max_length=20)
#     phone = forms.CharField(required=True, min_length=11, max_length=11)
#     course_name = forms.CharField(required=True, min_length=5, max_length=50)


# 给予model和Form的定义很相似，在某些情况下，可以直接把model转化成Form
class UserAskForm(forms.ModelForm):
    """
    既可以继承model中的字段，也可以新增字段，并且可以直接save()，它会调用model中的save，
    即在做了表单验证之后，直接把这个ModelForm调用save之后保存到数据库当中了，这个Form是所做不到的。
    """
    # my_field = forms.CharField()  # 可以添加新字段
    class Meta:
        # 指定把哪个model转换成ModelForm
        model = UserAsk
        # 指定需要用到model的哪些字段，即继承model中的哪些字段
        fields = ['name', 'mobile', 'course_name']

    def clean_mobile(self):
        """
        验证手机号码是否合法

        必须以clean开头，然后加下划线加字段名，这样在初始化UserAskForm时，会主动调用该方法，
        对这个字段做一个验证，该方法非常重要，它实际上是对每个字段进行进一层的自定义封装

        Form有一个内置的变量cleaned_data，把每个字段（field）clean之后放到cleaned_data里面
        """
        mobile = self.cleaned_data['mobile']
        REGEX_MOBILE = '^1[358]\d{9}$|^147\d{8}$|^176\d{8}$'
        p = re.compile(REGEX_MOBILE)
        if p.match(mobile):
            return mobile
        else:
            raise forms.ValidationError("手机号码非法", code='mobile_invalid')