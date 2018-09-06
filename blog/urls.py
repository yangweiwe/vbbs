from django.conf.urls import url
from blog import views

urlpatterns = [
    # 文章详情
    url(r'(.*)/article/(\d+)/$', views.article_detail),
    # 左侧分类
    url(r'(.*)/(tag|category|archive)/(.*)/$', views.home),
    # 个人文章页面
    url(r'(.*)/$', views.home),
]