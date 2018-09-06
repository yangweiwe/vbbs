"""bbs URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from blog import views
from django.views.static import serve
from bbs import settings
from blog import urls as blog_url

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^login/', views.login),
    url(r'^v_code/', views.v_code),
    url(r'^index/', views.index),

    url(r'^login2/', views.login2),
    # 极验科技 获取验证码的url
    url(r'^pcgetcaptcha/', views.pcgetcaptcha),

    # 注册url
    url(r'^register/',views.register),
    # media路由配置
    url(r'media/(?P<path>.*)$', serve, {"document_root":settings.MEDIA_ROOT}),
    # 退出url
    url(r'^logout/',views.logout),
    # 二级路由
    url(r'^blog/', include(blog_url)),
    # 点赞/反对路由
    url(r'^updown/$', views.updown),
    # 评论路由
    url(r'^comment/$', views.comment),

    # 后台管理
    url(r'backend/$',views.backend),
    # 添加文章
    url(r'add_article/$', views.add_article),
    # 文章图片处理
    url(r'upload_img/$', views.upload_img),
    # 删除文章修改文章
    url(r'^delete_article/(\d+)/$', views.delete_article),
    url(r'^edit_article/(\d+)/$', views.edit_article),


    # 以上都匹配不到，就匹配这个
    url(r'^$', views.index)

]


# if settings.DEBUG:
#     import debug_toolbar
#     urlpatterns = [
#         url(r'^__debug__/', include(debug_toolbar.urls)),
#     ] + urlpatterns
