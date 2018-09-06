from django import template

from blog import models

register = template.Library()


@register.inclusion_tag("left_tag.html")
def left_panel(username):
    user_obj = models.UserInfo.objects.filter(username=username).first()
    blog = user_obj.blog
    # 左侧分类菜单需要的那些数据
    # 查到当前用户所有的文章
    # data = models.Article.objects.filter(user__username=username)
    # 当前站点下的文章分类
    category_list = models.Category.objects.filter(blog=blog)
    # 当前站点下所有的文章标签
    tag_list = models.Tag.objects.filter(blog=blog)
    # 以日期来归档
    from django.db.models import Count
    ret = models.Article.objects.filter(user__username=username).extra(
        select={"create_time": "DATE_FORMAT(create_time, '%%Y-%%m')"}).values("create_time").annotate(
        num=Count("nid")).values("create_time", "num")
    return {
        "username": username,
        "category_list": category_list,
        "tag_list": tag_list,
        "create_time": ret
    }

