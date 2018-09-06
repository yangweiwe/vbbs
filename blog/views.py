import os

from django.conf import settings
from django.contrib import auth
from django.contrib.auth.views import login_required
from django.db import transaction
from django.db.models import F
from django.http import JsonResponse
from django.shortcuts import render, HttpResponse, redirect
from geetest import GeetestLib

from blog import forms, models

# Create your views here.

pc_geetest_id = "b46d1900d0a894591916ea94ea91bd2c"
pc_geetest_key = "36fc3fe98530eea08dfc6ce76e3d24c4"


# 滑动验证码加载所需要的函数
def pcgetcaptcha(request):
    user_id = 'test'
    gt = GeetestLib(pc_geetest_id, pc_geetest_key)
    status = gt.pre_process(user_id)
    request.session[gt.GT_STATUS_SESSION_KEY] = status
    request.session["user_id"] = user_id
    response_str = gt.get_response_str()
    return HttpResponse(response_str)


# 滑动 验证版登录
def login2(request):
    form_obj = forms.LoginForm()
    if request.method == "POST":
        gt = GeetestLib(pc_geetest_id, pc_geetest_key)
        challenge = request.POST.get(gt.FN_CHALLENGE, '')
        validate = request.POST.get(gt.FN_VALIDATE, '')
        seccode = request.POST.get(gt.FN_SECCODE, '')
        status = request.session[gt.GT_STATUS_SESSION_KEY]
        user_id = request.session["user_id"]
        if status:
            result = gt.success_validate(challenge, validate, seccode, user_id)
        else:
            result = gt.failback_validate(challenge, validate, seccode)
            # 如果验证码正确：
        if result:
            ret = {"code": 0}
            username = request.POST.get("username")
            password = request.POST.get("password")
            # 如果验证码正确
            user = auth.authenticate(username=username, password=password)
            if user:
                ret["data"] = "/index/"
            else:
                ret["code"] = 1
                ret["data"] = "用户名或密码错误"
            return JsonResponse(ret)
    return render(request, "login2.html", {"form_obj": form_obj})


def login(request):
    # 是否从别的页面跳转过来
    url = request.GET.get("next", "")
    form_obj = forms.LoginForm()
    if request.method == "POST":
        ret = {"code": 0}
        username = request.POST.get("username")
        password = request.POST.get("password")
        v_code = request.POST.get("v_code", "")
        if v_code.upper() == request.session.get("v_code", ""):
            # 如果验证码正确
            user = auth.authenticate(username=username, password=password)
            if user:
                auth.login(request, user)
                if not url:
                    ret["data"] = "/index/"
                    print(ret["data"])
                else:
                    ret["data"] = "http://127.0.0.1:8000{}".format(url)
                    print(ret["data"])

            else:
                ret["code"] = 1
                ret["data"] = "用户名或密码错误"
        else:
            ret["code"] = 1
            ret["data"] = "验证码错误"
        return JsonResponse(ret)
    return render(request, "login.html", {"form_obj": form_obj})


# 验证码
def v_code(request):
    from PIL import Image, ImageDraw, ImageFont
    import random
    # 定义一个生成随机颜色的函数
    def get_color():
        return random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)

    # 生成一个图片对象
    img_obj = Image.new(
        "RGB",
        (250, 35),
        color=get_color()
    )
    # 在图片中加文字
    # 生成一个画笔对象
    draw_obj = ImageDraw.Draw(img_obj)
    # 加载字体文字
    font_obj = ImageFont.truetype("static/font/kumo.ttf", size=28)

    # for 循环5次，每次写一个随机字符
    tmp_list = []
    for i in range(5):
        n = str(random.randint(0, 9))  # 生成一个随机数字
        l = chr(random.randint(97, 122))  # 生成一个随机小写字母
        u = chr(random.randint(65, 90))  # 生成一个随机大写字母
        r = random.choice([n, l, u])  # 随机选取
        tmp_list.append(r)  # 存入列表 为下面加入session做准备
        draw_obj.text(
            (i * 48 + 20, 0),  # 位置
            r,  # 内容
            get_color(),  # 颜色
            font=font_obj  # 字体
        )
        # 拿到随机验证码 拼接成字符串 存入session
    v_code_str = "".join(tmp_list)
    request.session["v_code"] = v_code_str.upper()

    # 加干扰线
    # width = 250  # 图片宽度（防止越界）
    # height = 35
    # for i in range(2):
    #     x1 = random.randint(0, width)
    #     x2 = random.randint(0, width)
    #     y1 = random.randint(0, height)
    #     y2 = random.randint(0, height)
    #     draw_obj.line((x1, y1, x2, y2), fill=get_color())
    #
    # # 加干扰点
    # for i in range(2):
    #     draw_obj.point([random.randint(0, width), random.randint(0, height)], fill=get_color())
    #     x = random.randint(0, width)
    #     y = random.randint(0, height)
    #     draw_obj.arc((x, y, x+4, y+4), 0, 90, fill=get_color())

    # 第一版： 将生成的图片保存到文件中
    # with open("xx.png", "wb") as f:
    #     img_obj.save(f, "png")
    # print("图片已经生成！")
    # with open("xx.png", "rb") as f:
    #     return HttpResponse(data, content_type="image/png")

    # 第二版 直接将图片保存在内存中
    from io import BytesIO
    tmp = BytesIO()  # 生成一个io 对象
    img_obj.save(tmp, "png")
    data = tmp.getvalue()
    return HttpResponse(data, content_type="image/png")


# 注册的函数
def register(request):
    form_obj = forms.ReForm()
    if request.method == "POST":
        ret = {"code": 0}
        form_obj = forms.ReForm(request.POST)
        if form_obj.is_valid():
            # 数据经过校验
            avatar_obj = request.FILES.get("avatar")
            form_obj.cleaned_data.pop("re_password")
            models.UserInfo.objects.create_user(
                avatar=avatar_obj,
                **form_obj.cleaned_data
            )
            ret["data"] = "/login/"
        else:
            # 数据没经过校验返回错误信息
            ret["code"] = 1,
            ret["data"] = form_obj.errors
        return JsonResponse(ret)
    return render(request, "register.html", {"form_obj": form_obj})


# 注销
def logout(request):
    auth.logout(request)
    return redirect("/index/")


# 主页面
def index(request):
    article_obj = models.Article.objects.all()
    from utils import mypage
    # 拿到总的数据量
    total_num = article_obj.count()
    # 拿到分页所在的url
    url_prefix = request.path_info.strip("/")
    # 拿到当前页
    current_page = request.GET.get("page")
    page_obj = mypage.Page(total_num, current_page, url_prefix, per_page=3)
    article_obj = article_obj[page_obj.data_start:page_obj.data_end]
    page_html = page_obj.page_html()
    return render(request, "index.html", {
        "article_obj": article_obj,
        "page_html": page_html
    })


# 个人博客主页面
def home(request, username, *args):
    # 根据传过来的参数来查找用户，拿到用户对象，如果不用first 来取就是一个QuerySet对象只有方法没有属性
    user_obj = models.UserInfo.objects.filter(username=username).first()
    if not user_obj:
        return HttpResponse("404")
    else:
        blog = user_obj.blog
    # # 当前站点下的文章分类
    # category_list = models.Category.objects.filter(blog=blog)
    # # 当前站点下所有的文章标签
    # tag_list = models.Tag.objects.filter(blog=blog)
    # # 以日期来归档
    # from django.db.models import Count
    # ret = models.Article.objects.filter(user__username=username).extra(
    #     select={"create_time": "DATE_FORMAT(create_time, '%%Y-%%m')"}).values("create_time").annotate(
    #     num=Count("nid")).values("create_time", "num")
    if not args:
        # 查到当前用户所有的文章
        data = models.Article.objects.filter(user__username=username)
    else:
        # tag | category | archive
        if args[0] == "tag":
            data = models.Article.objects.filter(user=user_obj).filter(tags__title=args[1])
        elif args[0] == "category":
            data = models.Article.objects.filter(user=user_obj).filter(category__title=args[1])
        else:
            year, month = args[1].split("-")
            data = models.Article.objects.filter(user=user_obj).filter(create_time__year=year, create_time__month=month)
        if not data:
            return HttpResponse("404 你访问的页面不存在")
    from utils import mypage
    # 拿到总的数据量
    total_num = data.count()
    # 拿到分页所在的url
    url_prefix = request.path_info.strip("/")
    # 拿到当前页
    current_page = request.GET.get("page")
    page_obj = mypage.Page(total_num, current_page, url_prefix, per_page=3)
    data = data[page_obj.data_start:page_obj.data_end]
    page_html = page_obj.page_html()
    return render(request, "home.html", {
        "username": username,
        "blog": blog,
        "article_list": data,
        "page_html": page_html
    })


# 文章详情页面
def article_detail(request, username, article_id):
    user_obj = models.UserInfo.objects.filter(username=username).first()
    if not user_obj:
        return HttpResponse("404")
    else:
        blog = user_obj.blog

    article_obj = models.Article.objects.filter(nid=article_id).first()
    comment_obj = models.Comment.objects.filter(article_id=article_id)
    return render(
        request, "article_detail.html", {
            "article": article_obj,
            "comment_obj": comment_obj,
            "blog": blog,
            "username": username
        }
    )


# 点赞和反对视图函数
def updown(request):
    ret = {"code": 0}
    is_up = request.POST.get("is_up")
    article_id = request.POST.get("article_id")
    user_id = request.user.nid
    is_up = True if is_up.upper() == "TRUE" else False
    # 判断这个用户是不是这篇文章的作者 如果是返回提示信息
    if models.Article.objects.filter(nid=article_id, user_id=user_id):
        # 当前文章的作者不可以给自己点赞或者点反对
        ret["code"] = 1
        ret["data"] = "不能给自己点赞" if is_up else "不可以反对自己的内容"
    else:
        # 判断这个用户是否已经给本篇文章点赞/反对
        is_exist = models.ArticleUpDown.objects.filter(user_id=user_id, article_id=article_id)
        if is_exist:
            ret["code"] = 1
            ret["data"] = "你已经点过赞了" if is_up else "你已经反对过了"
        else:
            # 进行数据库操作 开启事务，与文章表中的数据进行同步

            with transaction.atomic():
                # 创建点赞/反对记录
                models.ArticleUpDown.objects.create(
                    is_up=is_up,
                    user_id=user_id,
                    article_id=article_id
                )
                # 更新article表中对应的数据
                if is_up:
                    models.Article.objects.filter(nid=article_id).update(up_count=F("up_count") + 1)
                else:
                    models.Article.objects.filter(nid=article_id).update(down_count=F("down_count") + 1)
            ret["data"] = "点赞" if is_up else "反对"

    return JsonResponse(ret)


# 评论视图
def comment(request):
    ret = {"code": 0}
    user_id = request.user.pk
    comment = request.POST.get("comment")
    article_id = request.POST.get("article_id")
    pid = request.POST.get("pid", "")
    # 判断当前用户是否是 当前评论文章的作者，不是才让评论

    # 创建评论 开启事物
    with transaction.atomic():
        # 先创建一个评论记录
        obj = models.Comment.objects.create(
            user_id=user_id,
            article_id=article_id,
            content=comment,
            parent_comment_id=pid
        )
        # 更新Article comment_count字段数据
        models.Article.objects.filter(nid=article_id).update(
            comment_count=F("comment_count") + 1
        )
    ret["data"] = obj.nid
    return JsonResponse(ret)


# 后台管理视图
@login_required
def backend(request):
    article_obj = models.Article.objects.filter(user=request.user)
    return render(request, "backend.html", {"article_list": article_obj})


def add_article(request):
    if request.method == "POST":
        title = request.POST.get("title")
        content = request.POST.get("content")
        # 入库之前要做校验
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(content, "html.parser")
        for tag in soup.find_all("script"):
            # 找到每一个script标签，并删掉
            tag.decompose()
        # 去数据库中创建新文章，操作两张表：文章，与文章详情
        with transaction.atomic():
            article_obj = models.Article.objects.create(
                title=title,
                desc=soup.text[0:150],  # 根据文章内容做截取
                user=request.user
            )
            models.ArticleDetail.objects.create(
                content=soup.prettify(),  # 经过处理后的文本
                article=article_obj
            )
            return redirect("/backend/")

    return render(request, "add_article.html")


# kindeditor 接收上传文件的视图
def upload_img(request):
    # 把上传文件的文件保存在服务端上
    file_obj = request.FILES.get("imgFile")
    with open(os.path.join(settings.MEDIA_ROOT, "article_img", file_obj.name), 'wb') as f:
        # 从file_obj逐行读 往f里面一点一点写
        for chunk in file_obj.chunks():
            f.write(chunk)
    # 返回的相应格式要求
    ret = {"error": 0, "url": "/media/article_img/{}".format(file_obj.name)}
    return JsonResponse(ret)


def delete_article(request, delete_id):
    models.Article.objects.filter(nid=delete_id).delete()
    return redirect("/backend/")


def edit_article(request, edit_id):
    if request.method == "POST":
        if request.method == "POST":
            title = request.POST.get("title")
            content = request.POST.get("content")
            # 入库之前要做校验
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(content, "html.parser")
            for tag in soup.find_all("script"):
                # 找到每一个script标签，并删掉
                tag.decompose()
            # 去数据库中创建新文章，操作两张表：文章，与文章详情
            with transaction.atomic():
                article_obj = models.Article.objects.create(
                    title=title,
                    desc=soup.text[0:150],  # 根据文章内容做截取
                    user=request.user
                )
                models.ArticleDetail.objects.create(
                    content=soup.prettify(),  # 经过处理后的文本
                    article=article_obj
                )
                return redirect("/backend/")
    article_obj = models.Article.objects.filter(nid=edit_id).first()
    return render(request, "edit_article.html", {"article_obj": article_obj})
