__author__ = 'wqq'
__date__ = '2018/3/28 10:51'
import xadmin
from .models import Course, Lesson, Video, CourseResource, BannerCourse


class LessonInline(object):
    model = Lesson
    extra = 0


class CourseResourceInline(object):
    model = CourseResource
    extra = 0


class CourseAdmin(object):
    list_display = ['name', 'desc', 'detail', 'degree', 'learn_times', 'students', 'get_zj_nums', 'go_to']
    # 变量和函数对于Python来说都是一样的，list_display中写入函数get_zj_nums，
    # get_zj_nums是一个动态值，并不会保存在数据库当中，不过可以调用该函数，使其展现在列表中
    search_fields = ['name', 'desc', 'detail', 'degree', 'students']
    list_filter = ['name', 'desc', 'detail', 'degree', 'learn_times', 'students']
    ordering = ['-click_nums']
    readonly_fields = ['click_nums']
    exclude = ['fav_nums']
    # readonly_fields、exclude这两个字段是冲突的，如果readonly_fields有fav_nums该字段，
    # 再在exclude中写该字段fav_nums，是不生效的，照样显示出来
    inlines = [LessonInline, CourseResourceInline]
    # 完成课程里面嵌套章节和视频资源，但只能做一层嵌套，即不能再在此页面中的章节里嵌套视频Video，不过可以在章节管理中嵌套视频Video
    list_editable = ['desc', 'degree']  # 在表列页就可以修改这些字段值，不用点进去
    refresh_times = [3, 4, 5]  # 定时刷新，里面的数值可能取值，单位是秒

    def queryset(self):
        qs = super(CourseAdmin, self).queryset()
        qs = qs.filter(is_banner=False)  # 自定义列表页的访问数据
        return qs


class BannerCourseAdmin(object):
    list_display = ['name', 'desc', 'detail', 'degree', 'learn_times', 'students']
    search_fields = ['name', 'desc', 'detail', 'degree', 'students']
    list_filter = ['name', 'desc', 'detail', 'degree', 'learn_times', 'students']
    ordering = ['-click_nums']
    readonly_fields = ['click_nums']
    exclude = ['fav_nums']
    inlines = [LessonInline, CourseResourceInline]

    def queryset(self):
        qs = super(BannerCourseAdmin, self).queryset()
        qs = qs.filter(is_banner=True)  # 自定义列表页的访问数据
        return qs


class LessonAdmin(object):
    list_display = ['course', 'name', 'add_time']
    search_fields = ['course', 'name']
    list_filter = ['course__name', 'name', 'add_time']


class VideoAdmin(object):
    list_display = ['lesson', 'name', 'add_time']
    search_fields = ['lesson', 'name']
    list_filter = ['lesson', 'name', 'add_time']


class CourseResourceAdmin(object):
    list_display = ['course', 'name', 'download', 'add_time']
    search_fields = ['course', 'name', 'download']
    list_filter = ['course', 'name', 'download', 'add_time']


xadmin.site.register(Course, CourseAdmin)
xadmin.site.register(BannerCourse, BannerCourseAdmin)
xadmin.site.register(Lesson, LessonAdmin)
xadmin.site.register(Video, VideoAdmin)
xadmin.site.register(CourseResource, CourseResourceAdmin)

