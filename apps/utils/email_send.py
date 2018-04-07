__author__ = 'wqq'
__date__ = '2018/3/29 20:31'
from random import Random
from django.core.mail import send_mail

from users.models import EmailVerifyRecord
from wqqOnline.settings import EMAIL_FROM


def send_register_email(email, send_type="register"):
    email_record = EmailVerifyRecord()
    # 这个code很关键，邮箱验证码的功能是如何完成的？
    # 一般情况下，会在用户的链接里面给它加一个随机字符串，这个随机字符串是后台生成的，
    # 这个code就是随机字符串，别人是没法伪造的
    # 把随机字符串加到url链接里面，用户在点击链接的时候，把code取出来，然后再回来查询数据库
    # 如果存在就给它激活，否则报错
    if send_type == 'update_email':
        code = random_str(4)
    else:
        code = random_str(16)
    email_record.code = code
    email_record.email = email
    email_record.send_type = send_type
    email_record.save()

    email_title =''
    email_boby = ''

    if send_type == "register":
        email_title = "慕学在线网注册激活链接"
        email_boby = "请点击下面的链接激活你的账号：http://127.0.0.1:8000/active/{0}".format(code)

        send_status = send_mail(email_title, email_boby, EMAIL_FROM, [email])
        if send_status:
            pass
    elif send_type == 'forget':
        email_title = "慕学在线网注册密码重置链接"
        email_boby = "请点击下面的链接重置密码：http://127.0.0.1:8000/reset/{0}".format(code)

        send_status = send_mail(email_title, email_boby, EMAIL_FROM, [email])
        if send_status:
            pass
    elif send_type == 'update_email':
        email_title = "慕学在线邮箱修改验证码"
        email_boby = "你的邮箱验证码为：{0}".format(code)

        send_status = send_mail(email_title, email_boby, EMAIL_FROM, [email])
        if send_status:
            pass

def random_str(randomlength=8):
    """
    生成随机字符串，把这个当作发送邮箱激活链接中的字符串
    """
    str = ''
    chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
    length = len(chars) - 1
    random = Random()
    for i in range(randomlength):
        str += chars[random.randint(0, length)]
    return str
