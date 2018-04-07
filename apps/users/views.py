from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from django.views.generic.base import View
from django.contrib.auth.hashers import make_password
from django.http import HttpResponse, HttpResponseRedirect
import json
from pure_pagination import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse

from .models import UserProfile, EmailVerifyRecord
from .forms import LoginForm, RegisterForm, ForgetForm, ModifyPwdForm, UploadImageForm
from .forms import UploadInfoForm
from utils.email_send import send_register_email
from utils.mixin_utils import LoginRequiredMixin
from operation.models import UserCourse, UserFavorite, UserMessage
from organization.models import CourseOrg, Teacher
from courses.models import Course
from .models import Banner

# Create your views here.


class CustomBackend(ModelBackend):
    def authenticate(self, username=None, password=None, **kwargs):
        try:
            user = UserProfile.objects.get(Q(username=username)|Q(email=username))
            # 不搜索密码，是因为django在存储密码的时候实际上存储的是密文，没法用明文去查询的，所以不能用password=password。
            if user.check_password(password):
                # UserProfile继承了AbstractUser，AbstractUser继承了AbstractBaseUser和PermissionsMixin，
                # AbstractBaseUser中有一个方法check_password(self, raw_password)
                return user
        except Exception as e:
            return None


class ActiveUserView(View):
    def get(self, request, active_code):
        all_records = EmailVerifyRecord.objects.filter(code=active_code)
        if all_records:
            for record in all_records:
                email = record.email
                user = UserProfile.objects.get(email=email)
                user.is_active = True
                user.save()
        else:
            return render(request, "active_fail.html")
        return render(request, "login.html")


class RegisterView(View):
    def get(self, request):
        register_form = RegisterForm()
        return render(request, 'register.html', {'register_form': register_form})
        # 这个Form实际上我们在把它生成字符串的时候，它是会生成一段html代码的，
        # 比如说EmailField、CaptchaField实际上会生成一个input框，不同的Field会生成不同的html代码

    def post(self, request):
        register_form = RegisterForm(request.POST)
        if register_form.is_valid():
            user_name = request.POST.get("email", '')
            if UserProfile.objects.filter(email=user_name):
                return render(request, 'register.html', {'register_form': register_form, 'msg': "用户已经存在"})
            pass_word = request.POST.get('password', '')
            user_profile = UserProfile()
            user_profile.username = user_name
            user_profile.email = user_name
            user_profile.is_active = False
            user_profile.password = make_password(pass_word)
            user_profile.save()

            # 写入欢迎注册消息
            user_message = UserMessage()
            user_message.user = user_profile.id
            user_message.message = "欢迎注册慕学在线网"
            user_message.save()

            send_register_email(user_name, "register")
            return render(request, 'login.html', {})
        else:
            return render(request, 'register.html', {'register_form': register_form})


class ForgetPwdView(View):
    def get(self, request):
        forget_form = ForgetForm()
        return render(request, "forgetpwd.html", {'forget_form': forget_form})

    def post(self, request):
        forget_form = ForgetForm(request.POST)
        if forget_form.is_valid():
            email = request.POST.get('email', '')
            send_register_email(email, 'forget')
            return render(request, 'send_success.html')
        else:
            return render(request, "forgetpwd.html", {'forget_form': forget_form})


class ResetView(View):
    def get(self, request, active_code):
        all_records = EmailVerifyRecord.objects.filter(code=active_code)
        if all_records:
            for record in all_records:
                email = record.email
                return render(request, "password_reset.html", {'email': email})
        else:
            return render(request, "active_fail.html")


class ModifyPwdView(View):
    """
    修改用户密码（在未登录的状态下）
    """
    def post(self, request):
        modify_form = ModifyPwdForm(request.POST)
        if modify_form.is_valid():
            pwd1 = request.POST.get('password1', '')
            pwd2 = request.POST.get('password2', '')
            email = request.POST.get('email', '')
            if pwd1 != pwd2:
                return render(request, "password_reset.html", {'email': email, "msg": "密码不一致"})
            user = UserProfile.objects.get(email=email)
            user.password = make_password(pwd2)
            user.save()
            return render(request, "login.html")
        else:
            email = request.POST.get('email', '')
            return render(request, "password_reset.html", {'email': email, "modify_form": modify_form})


class LogoutView(View):
    """
    用户登出
    """
    def get(self, request):
        logout(request)
        return HttpResponseRedirect(reverse("index"))
        # reverse可以把url名称直接反解成整个url地址，然后供HttpResponseRedirect调用


class LoginView(View):
    """
    不需要判断request.method的取值，django的View根据request.method会自动相应的方法
    """
    def get(self, request):
        return render(request, 'login.html', {})

    def post(self, request):
        login_form = LoginForm(request.POST)
        # 用这个类LoginForm实例化时_errors的初始值是None，
        # login_form.is_valid()将判断给出的字段值是否满足要求，如不满足要求，_error会被附上新值（错误）
        if login_form.is_valid():
            user_name = request.POST.get("username", '')
            pass_word = request.POST.get('password', '')
            user1 = authenticate(username=user_name, password=pass_word)
            """
            authenticate向数据库发起验证，验证用户名和密码是否正确，
            如果认证通过，返回一个users的model，失败返回None，但并没有进行登陆只是验证
    
            authenticate只能验证用户名和密码是否正确，不过django提供了一种方法，让我们可以自定义后台authenticate认证方法，
            1. 在settings.py中重载一个变量AUTHENTICATION_BACKENDS，该函数和之前函数返回的都是一样的，是一个usermodel
            2. 在users.views中定义一个继承auth.backends.ModelBackend的类CustomBackend，
            auth.backends.ModelBackend这个类有一个方法（authenticate）会被django自动调用
    
            """
            if user1 is not None:
                if user1.is_active:
                    login(request, user1)
                    # login之前，request.user是AnonymousUser，login之后request.user就是user1，其实他就是UserProfile的值
                    """
                    调用login即可完成登陆，调用login时，django会对request进行一部分操作，
                    在request中写入了一些东西
                    """
                    # 登陆之后，首页变了，是因为用了render，当使用render时，因为木有数据传过来，所以一片空白
                    # 为解决这个问题，用HttpResponseRedirect
                    # return render(request, 'index.html')
                    return HttpResponseRedirect(reverse("index"))
                else:
                    return render(request, 'login.html', {'msg': "用户未激活"})
            else:
                return render(request, 'login.html', {'msg': "用户名或密码错误"})
        else:
            return render(request, 'login.html', {"login_form": login_form})

"""
    login()根据用户的信息生产了一个session_id，这个session_id是必须保存在数据库当中的，
    在数据表django_session当中这个值保存为session_key,返回给浏览器保存为sessionid
    因为用户登陆之后，它需要查询取出用户的基本信息，
    django_Session这个表实际上就是用来存储django给每个用户生成的一个session信息比如说session_id，
    实际上django在存储用户信息的时候，它会对用户信息进行加密，生产一个session_data                     
                
    一旦把这个sessionid放到cookie当中，以后每次对这个网站的任何页面进行访问的时候，
    它都会把这个sessionid带过来，带到服务器，这样服务器就不需要知道用户名和密码就能知道是哪个用户，

    为了理解这个session到底是django的哪一部分做成的，
    比如说浏览器带了一个sessionid，django是怎么把这个sessionid转换成user的，
    这是因为django在settings.py当中有一个配置：INSTALL_APPS里面有一个django.contrib.sessions,
    django.contrib.sessions这个app它会对每次request或reponse请求做拦截的，
    它拦截到浏览器过来的request的时候，就会在里面找到sessionid，找到sessionid之后，它通过sessionid来数据表django_session进行查询，
    查询到了他就知道原来是有user的，它再做解密，把这个session_data取出来，这个session_data里面实际上存储了很多用户的信息，
    所以说它就直接把这个user给取出来了，
    
    也就是django通过django.contrib.sessions这个组件，在每次浏览器请求的时候，它就已经把我们request当中给做了一定处理，
    比如说把我们的user给放进来，以及在返回的时候，它也是会把response（返回给浏览器的东西）主动加上sessionid，
    所以说这个sessionid很重要，它是默认给我们配置好的，如果把django.contrib.sessions注释掉，自动登陆就会失效
    
    cookie:实际上是浏览器的一种本地存储机制，跟服务器是没有关系的，它可以存储任何键值对，
    比如说，存储用户名和密码，存储服务器给我们返回的任何信息，不过这个键值对是存储在某个域名之下的，
    每个域名下的key和value是不能互相访问的，存储了这些信息之后，浏览器在每次发送请求的时候，
    它就会把这个域名当中的cookie所有值发送到服务器，这样服务器就可以通过cookie看到浏览器自带了一些信息过来，
    这些信息实际上也是之前服务器返回给浏览器的，或者是用户填写的信息，这就是cookie的机制。
    
    但是cookie有一种不安全性，就是说你不能用户的所有信息都存储在本地吧，一旦被窃取了，别人就能知道你的用户名和密码，
    给予这种考虑，服务器在返回这个id的时候，它用到了一种session机制，就是根据用户名和密码生成了一段随机字符串，
    这段字符串是有过期时间的，这个session是由服务器生成的，它是存储在服务器端的，然后它把这个session发给用户，
    用户存储在cookie当中，然后在做下一次请求的时候，用户把cookie当中的信息也就是session给带回给服务器，
    服务器通过这个sessionid在数据库中查询该用户是哪个用户，它就可以对这个用户做标记，
    这样的话，django就利用了cookie和session的机制完成了自动登陆
"""
# def user_login(request):
#     if request.method == 'POST':
#         user_name = request.POST.get("username", '')
#         pass_word = request.POST.get('password', '')
#         user1 = authenticate(username=user_name, password=pass_word)
#         """
#         authenticate向数据库发起验证，验证用户名和密码是否正确，
#         如果认证通过，返回一个users的model，失败返回None，但并没有进行登陆只是验证
#
#         authenticate只能验证用户名和密码是否正确，不过django提供了一种方法，让我们可以自定义后台authenticate认证方法，
#         1. 在settings.py中重载一个变量AUTHENTICATION_BACKENDS，该函数和之前函数返回的都是一样的，是一个usermodel
#         2. 在users.views中定义一个继承auth.backends.ModelBackend的类CustomBackend，
#         auth.backends.ModelBackend这个类有一个方法（authenticate）会被django自动调用
#
#         """
#         if user1 is not None:
#             login(request, user1)
#             # login之前，request.user是AnonymousUser，login之后request.user就是user1
#             """
#             调用login即可完成登陆，调用login时，django会对request进行一部分操作，
#             在request中写入了一些东西
#             """
#             return render(request, 'index.html')
#         else:
#             return render(request, 'login.html', {'msg': "用户名或密码错误"})
#
#     elif request.method == "GET":
#         return render(request, 'login.html', {})


class UserinfoView(LoginRequiredMixin, View):
    """
    用户个人信息
    """
    def get(self, request):
        return render(request, 'usercenter-info.html', {})

    def post(self, request):
        user_info_form = UploadInfoForm(request.POST, instance=request.user)
        # 这是用于修改，需要用instance指定是用哪个实例，才可以做修改，
        # 如果不指定该参数，默认save时新增加一个用户
        if user_info_form.is_valid():
            user_info_form.save()
            return HttpResponse('{"status": "success"}', content_type='application/json')
        else:
            return HttpResponse(json.dumps(user_info_form.errors), content_type='application/json')


class UploadImageView(LoginRequiredMixin, View):
    """
    用户修改头像
    """
    def post(self, request):
        """
        在django的xadmin或admin当中，它实际上是可以对form定义为文件的时候（type=file)，
        可以对上传的文件自动保存
        """
        image_form = UploadImageForm(request.POST, request.FILES)
        """
        因为文件类型和在传递input时，在django中是放在两个不同的地方
        文件放在request.FILES
        """
        # if image_form.is_valid():
        #     image = image_form.cleaned_data['image']
        #     request.user.image = image
        #     request.user.save()

        # 上面四行代码与下面三行代码等价
        image_form = UploadImageForm(request.POST, request.FILES, instance=request.user)
        if image_form.is_valid():
            image_form.save()
            return HttpResponse('{"status": "success"}', content_type='application/json')
        else:
            return HttpResponse('{"status": "fail"}', content_type='application/json')


class UpdatePwdView(View):
    """
    在个人中心修改用户密码（登录的状态下）
    """
    def post(self, request):
        modify_form = ModifyPwdForm(request.POST)
        if modify_form.is_valid():
            pwd1 = request.POST.get('password1', '')
            pwd2 = request.POST.get('password2', '')
            if pwd1 != pwd2:
                return HttpResponse('{"status": "fail", "msg": "密码不一致"}', content_type='application/json')
            user = request.user
            user.password = make_password(pwd2)
            user.save()
            return HttpResponse('{"status": "success"}', content_type='application/json')
        else:
            return HttpResponse(json.dumps(modify_form.errors), content_type='application/json')


class SendEmailCodeView(LoginRequiredMixin, View):
    """
    发送邮箱验证码
    """
    def get(self, request):
        email = request.GET.get('email', '')

        if UserProfile.objects.filter(email=email):
            return HttpResponse('{"email": "邮箱已经存在"}', content_type='application/json')
        send_register_email(email, "update_email")
        return HttpResponse('{"status": "success"}', content_type='application/json')


class UpdateEmailView(LoginRequiredMixin, View):
    """
    修改个人邮箱
    """
    def post(self, request):
        email = request.POST.get('email', '')
        code = request.POST.get('code', '')
        existed_records = EmailVerifyRecord.objects.filter(email=email, code=code, send_type='update_email')
        if existed_records:
            user = request.user
            user.email = email
            user.save()
            return HttpResponse('{"status": "success"}', content_type='application/json')

        else:
            return HttpResponse('{"email": "验证码出错"}', content_type='application/json')


class MyCourseView(LoginRequiredMixin, View):
    """
    我的课程
    """
    def get(self, request):
        user_courses = UserCourse.objects.filter(user=request.user)
        return render(request, 'usercenter-mycourse.html', {
            "user_courses": user_courses
        })


class MyFavOrgView(LoginRequiredMixin, View):
    """
    我收藏的课程机构
    """
    def get(self, request):
        org_list = []
        fav_orgs = UserFavorite.objects.filter(user=request.user, fav_type=2)
        for fav_org in fav_orgs:
            org_id = fav_org.fav_id
            org = CourseOrg.objects.get(id=org_id)
            org_list.append(org)
        return render(request, 'usercenter-fav-org.html', {
            "org_list": org_list
        })


class MyFavTeacherView(LoginRequiredMixin, View):
    """
    我收藏的授课讲师
    """
    def get(self, request):
        teacher_list = []
        fav_teachers = UserFavorite.objects.filter(user=request.user, fav_type=3)
        for fav_teacher in fav_teachers:
            teacher_id = fav_teacher.fav_id
            org = Teacher.objects.get(id=teacher_id)
            teacher_list.append(org)
        return render(request, 'usercenter-fav-teacher.html', {
            "teacher_list": teacher_list
        })


class MyFavCourseView(LoginRequiredMixin, View):
    """
    我收藏的课程
    """
    def get(self, request):
        course_list = []
        fav_courses = UserFavorite.objects.filter(user=request.user, fav_type=1)
        for fav_course in fav_courses:
            course_id = fav_course.fav_id
            org = Course.objects.get(id=course_id)
            course_list.append(org)
        return render(request, 'usercenter-fav-course.html', {
            "course_list": course_list
        })


class MymessageView(LoginRequiredMixin, View):
    """
    我的消息
    """
    def get(self, request):
        all_messages = UserMessage.objects.filter(user=request.user.id)

        # 用户进入个人消息后清空未读消息的记录
        all_unread_messages = UserMessage.objects.filter(user=request.user.id, has_read=False)
        for unread_message in all_unread_messages:
            unread_message.has_read = True
            unread_message.save()

        # 对个人消息进行分页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1

        # Provide Paginator with the request object for complete querystring generation

        p = Paginator(all_messages, 1, request=request)

        messages = p.page(page)
        return render(request, 'usercenter-message.html', {
            "messages": messages
        })


class IndexView(View):
    """
    慕学在线网 首页
    """
    def get(self, request):
        # 取出轮播图
        all_banners = Banner.objects.all().order_by("index")
        courses = Course.objects.filter(is_banner=False)[:6]
        banner_courses = Course.objects.filter(is_banner=False)[:3]
        course_orgs = CourseOrg.objects.all()[:15]
        return render(request, 'index.html', {
            "all_banners": all_banners,
            "courses": courses,
            "banner_courses": banner_courses,
            "course_orgs": course_orgs
        })


def page_not_found(request):
    # 全局404处理函数
    from django.shortcuts import render_to_response
    response = render_to_response('404.html', {})
    response.status_code = 404
    return response
