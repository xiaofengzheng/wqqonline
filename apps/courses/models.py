from datetime import datetime

from django.db import models
from organization.models import CourseOrg, Teacher

# Create your models here.


class Course(models.Model):
    course_org = models.ForeignKey(CourseOrg, verbose_name="课程机构", null=True, blank=True)
    """
    指定null = True, blank = True，因为新增该字段时，数据库中已经有了一个Course实例了，
    如果新增的这个字段不能为空，它就会提示说以往的数据怎么办，以往数据的外键到底是什么，
    为了不造成这种结果，所以指定允许为空
    """
    name = models.CharField(max_length=50, verbose_name="课程名")
    desc = models.CharField(max_length=300, verbose_name="课程描述")
    detail = models.TextField(verbose_name="课程详情")
    # teacher = models.ForeignKey(Teacher, verbose_name="讲师", default="")
    is_banner = models.BooleanField(default=False, verbose_name="是否轮播")
    teacher = models.ForeignKey(Teacher, verbose_name="讲师", null=True, blank=True)
    degree = models.CharField(verbose_name="难度", choices=(("cj", "初级"), ("zj", "中级"), ("gj", "高级")), max_length=2)
    learn_times = models.IntegerField(default=0, verbose_name="学习时长（分钟数）")
    students = models.IntegerField(default=0, verbose_name="学习人数")
    fav_nums = models.IntegerField(default=0, verbose_name="收藏人数")
    image = models.ImageField(upload_to="courses/%Y/%m", verbose_name="封面图", max_length=100)
    click_nums = models.IntegerField(default=0, verbose_name="点击数")
    category= models.CharField(default="后端开发", max_length=20, verbose_name="课程类别")
    tag = models.CharField(default='', verbose_name="课程标签", max_length=10)
    youneed_know = models.CharField(default="",max_length=300, verbose_name="课程须知")
    teacher_tell = models.CharField(max_length=300, default="", verbose_name="老师告诉你")
    add_time = models.DateTimeField(default=datetime.now, verbose_name="添加时间")

    class Meta:
        verbose_name = "课程"
        verbose_name_plural = verbose_name

    def get_zj_nums(self):
        """
        获取课程章节数
        """
        return self.lesson_set.all().count()

    def get_learn_users(self):
        return self.usercourse_set.all()[:5]

    def get_course_lesson(self):
        """
        获取课程所有章节
        """
        return self.lesson_set.all()
    get_zj_nums.short_description = "章节数"  # 在列表页中的显示名称

    def go_to(self):
        from django.utils.safestring import mark_safe
        return mark_safe("<a href='http://www.projectsedu.com'>跳转</a>")
    go_to.short_description = "跳转"

    def __str__(self):
        return self.name


class BannerCourse(Course):
    class Meta:
        verbose_name ="轮播课程"
        verbose_name_plural = verbose_name
        proxy = True
        # 一定要设置proxy = True，因为如果继承Course而不设置proxy = True，则会再生成一张表
        # 设置proxy = True的话不会再生成一张表，并且具有Model的功能
        # 继承Course只是为了让同一个model（这里是Course）注册两个管理器，
        # 另外还需在adminx中增加些设置（包括重载queryset方法）
        # 最终效果：轮播数据由BannerCourseAdmin（轮播课程）来管理，非轮播数据由CourseAdmin（课程）来管理
        # 其实轮播数据和非轮播数据都在同一个model即同一张表中，在后台展现为了两张表，数据库中只有一张表


class Lesson(models.Model):
    course = models.ForeignKey(Course, verbose_name="课程")
    name = models.CharField(max_length=100, verbose_name="章节名")
    add_time = models.DateTimeField(default=datetime.now, verbose_name="添加时间")

    class Meta:
        verbose_name = "章节"
        verbose_name_plural = verbose_name

    def get_lesson_video(self):
        """
        获取章节视频
        """
        return self.video_set.all()

    def __str__(self):
        return self.name


class Video(models.Model):
    lesson = models.ForeignKey(Lesson, verbose_name="章节")
    name = models.CharField(max_length=100, verbose_name="视频名")
    learn_times = models.IntegerField(default=0, verbose_name="学习时长（分钟数）")
    url = models.CharField(max_length=200, verbose_name="访问地址", default="")
    add_time = models.DateTimeField(default=datetime.now, verbose_name="添加时间")

    class Meta:
        verbose_name = "视频"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class CourseResource(models.Model):
    course = models.ForeignKey(Course, verbose_name="课程")
    name = models.CharField(max_length=100, verbose_name="名称")
    download = models.FileField(upload_to="courses/resource/%Y/%m", verbose_name="资源文件", max_length=100)
    add_time = models.DateTimeField(default=datetime.now, verbose_name="添加时间")

    class Meta:
        verbose_name = "课程资源"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name
