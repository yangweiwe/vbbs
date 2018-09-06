from django import forms
from blog import models
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError

class LoginForm(forms.Form):
    username = forms.CharField(
        label="用户名",
        max_length=12,
        min_length=3,
        error_messages={
            "required": "用户名不能为空",
            "min_length": "用户名不得小于3位",
            "max_length": "用户名不得大于12位"
        },
        widget=forms.widgets.TextInput(
            attrs={"class":"form-control"}
        )
    )
    password = forms.CharField(
        label="密码",
        max_length=12,
        min_length=4,
        error_messages={
            "required": "密码不能为空",
            "min_length": "密码不得少于4位",
            "max_length": "密码不得大于12位"
        },
        widget=forms.widgets.PasswordInput(
          attrs={"class":"form-control"}
        )
    )


# 注册验证的form类
class ReForm(forms.Form):
    username = forms.CharField(
        label="用户名",
        max_length=12,
        min_length=4,
        error_messages={
            "required": "账户名不能为空",
            "min_length": "不得少于4位字符",
            "max_length": "最多不得超过12位",
        },
        widget=forms.widgets.TextInput(
            attrs={"class":"form-control", "placeholder":"用户名"}
        )
    )

    password = forms.CharField(
        label="密码",
        max_length=16,
        min_length=3,
        error_messages={
            "required":"密码不能为空",
            "min_length": "密码最少3位",
            "max_length": "密码最大16位",
        },
        widget=forms.PasswordInput(
            attrs={"class":"form-control", "placeholder":"密码"}
        )
    )

    re_password = forms.CharField(
        label="确认密码",
        max_length=16,
        min_length=3,
        error_messages={
            "required":"确认密码不能为空",
            "min_length": "最少3位",
            "max_length": "最大16位",
        },
        widget=forms.PasswordInput(
            attrs={"class":"form-control",  "placeholder":"确认密码"}
        )
    )

    phone = forms.CharField(
        label="手机号",
        min_length=11,
        max_length=11,
        validators=[
            RegexValidator(r'\d{11}$', "手机号必须为数字"),
            RegexValidator(r'^1[356789][0-9]{9}$', "手机号格式不正确"),
        ],
        error_messages={
            "required": "手机号不能为空",
            "min_length": "手机号是11位哟",
            "max_length": "手机号是11位哟"
        },
        widget=forms.widgets.TextInput(
            attrs={"class": "form-control",  "placeholder":"手机号"}
        )
    )


    # 定义验证用户名的 局部钩子函数
    def clean_username(self):
        value = self.cleaned_data.get("username","")
        if "金瓶梅" in value:
            raise ValidationError("用户名包含敏感词汇%s"%("金瓶梅"))
        elif models.UserInfo.objects.filter(username=value):
            raise ValidationError("用户名已存在")
        else:
            return value

    # 验证手机号是否已被注册的钩子函数
    def clean_phone(self):
        value = self.cleaned_data.get("phone", "")
        if models.UserInfo.objects.filter(phone=value):
            raise ValidationError("该手机号已经被使用")
        return value

    # 定义用于检验两次密码是否一致的全局钩子函数
    def clean(self):
        pwd = self.cleaned_data.get("password")
        re_pwd = self.cleaned_data.get("re_password")
        if re_pwd and pwd and pwd == re_pwd:
            return self.cleaned_data
        else:
            error = "两次密码不一致"
            self.add_error("re_password", error)
            raise ValidationError(error)

