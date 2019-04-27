from __future__ import unicode_literals
from django.shortcuts import render, redirect, reverse, HttpResponse

# Create your views here.
from django.core.paginator import Paginator, EmptyPage
from app01 import models

from django.contrib import auth
import random
from django.http import JsonResponse

from rest_framework.views import APIView
# ---------------------------------
from pyecharts import Map
from pyecharts import Pie

REMOTE_HOST = "https://pyecharts.github.io/assets/js"


# ---------------------------------
def home(request):
    return render(request, 'home.html')

def login_auth(func):
    def inner(request, *args, **kwargs):
        next_url = request.get_full_path()
        user = request.session.get('userid')
        if user:
            return func(request, *args, **kwargs)
        else:
            return redirect('/login/?next=%s' % next_url)

    return inner

class Login(APIView):
    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):
        response = {'status': None, 'msg': None, 'genre': None, 'name': None}
        name = request.POST.get('name')
        pwd = request.POST.get('pwd')
        type = request.POST.get('type')
        response['genre'] = type
        if type == 'admin':
            user = models.SuperUser.objects.filter(name=name, password=pwd).first()
            if user:

                response['status'] = 100
                response['msg'] = '登录成功'
                response['name'] = str(user)
            else:
                response['status'] = 101
                response['msg'] = '用户名或密码错误'
        elif type == 'teacher':
            user = models.Teacher.objects.filter(teacher_number=name, password=pwd).first()
            if user:
                response['status'] = 100
                response['msg'] = '登录成功'
                response['name'] = str(user)
            else:
                response['status'] = 101
                response['msg'] = '用户名或密码错误'

        elif type == 'student':
            user = models.Student.objects.filter(student_number=name, password=pwd).first()
            if user:
                response['status'] = 100
                response['msg'] = '登录成功'

            else:
                response['status'] = 101
                response['msg'] = '用户名或密码错误'
        else:
            response['msg'] = '用户类型错误'
        if response['status'] == 100:
            request.session['userid'] = user.pk
            request.session['user_type'] = type
        return JsonResponse(response)


def logout(request):
    request.session.flush()
    return render(request, 'login.html')


def update_password(request):
    if request.method == 'GET':
        return render(request, 'update_password.html')
    else:
        print(request.user_obj)
        userpassword = request.user_obj.password
        print(userpassword)
        err_msg = ''
        if request.method == 'POST':
            old_password = request.POST.get('old_password', '')
            new_password = request.POST.get('new_password', '')
            repeat_password = request.POST.get('repeat_password', '')
            # 检查旧密码是否正确
            if userpassword == old_password:
                if not new_password:
                    err_msg = '新密码不能为空'
                elif new_password != repeat_password:
                    err_msg = '两次密码不一致'
                else:
                    user_type = request.session.get('user_type')
                    user_id = request.session.get('userid')
                    if user_type == 'teacher':
                        models.Teacher.objects.filter(id=user_id).update(password=new_password)
                    elif user_type == 'student':
                        models.Student.objects.filter(id=user_id).update(password=new_password)
                    else:
                        models.SuperUser.objects.filter(id=user_id).update(password=new_password)

                    return redirect("/login/")
            else:
                err_msg = '原密码输入错误'
        # content = {
        #     'err_msg': err_msg,
        # }
        return render(request, 'update_password.html', {'err_msg': err_msg})

def get_random(name):
    import hashlib
    import time
    md = hashlib.md5()
    md.update(bytes(str(time.time()), encoding='utf-8'))
    md.update(bytes(name, encoding='utf-8'))
    return md.hexdigest()

# ---------------------------------

@login_auth
def student_list(request):
    # student_list=models.Student.objects.all()
    student_list = models.Student.objects.get_queryset().order_by('id')
    paginator = Paginator(student_list, 10)
    # 如果页码数多,让它显示前5,后5,中间是当前在的页码
    try:
        current_page_num = int(request.GET.get('page', 1))
        current_page = paginator.page(current_page_num)
        # print(current_page.object_list)
        # 总页码数,大于11的时候
        if paginator.num_pages > 11:
            # 当前页码数-5大于1的时候,page_range应该是?
            if current_page_num - 5 < 1:
                page_range = range(1, 12)
            elif current_page_num + 5 > paginator.num_pages:
                #     当前页码数+5大于总页码数,总页码数往前推11个
                page_range = range(paginator.num_pages - 10, paginator.num_pages + 1)
            else:
                page_range = range(current_page_num - 5, current_page_num + 6)
        else:
            # 小于11,有多少页,就显示多少页
            page_range = paginator.page_range
    except Exception as e:
        current_page_num = 1
        current_page = paginator.page(current_page_num)

    return render(request, 'student_list.html', locals())
    # return  render(request,'student_list.html',{'student_list':student_list})

@login_auth
def student_delete(request):
    if request.method == 'GET':
        id = request.GET.get('id')
        models.Student.objects.get(id=id).delete()
        url = reverse('student_list')
        return redirect(url)

@login_auth
def student_add(request):
    if request.method == 'GET':
        pclass_list = models.Professionalclass.objects.all()
        student = models.Student.objects.all()
        return render(request, 'student_add.html', locals())
    else:
        student_number = request.POST.get('student_number')
        name = request.POST.get('name')
        sex = request.POST.get('sex')
        pclass = request.POST.get('pclass')
        nation = request.POST.get('nation')
        birthday = request.POST.get('birthday')
        birthplace = request.POST.get('birthplace')
        models.Student.objects.create(student_number=student_number, name=name, sex=sex, pclass_id=pclass,
                                      nation=nation, birthday=birthday, birthplace=birthplace)
        return redirect('/student_list/')

@login_auth
def student_update(request):
    if request.method == 'GET':
        id = request.GET.get('id')
        # print(id)
        # student=models.Student.objects.filter(id=id).first()
        student = models.Student.objects.get(id=id)
        print(student)
        pclass_list = models.Professionalclass.objects.all()
        return render(request, 'student_update.html', locals())
    else:
        id = request.GET.get('id')
        student_number = request.POST.get('student_number')
        name = request.POST.get('name')
        sex = request.POST.get('sex')
        pclass = request.POST.get('pclass')
        nation = request.POST.get('nation')
        birthday = request.POST.get('birthday')
        birthplace = request.POST.get('birthplace')
        models.Student.objects.filter(id=id).update(student_number=student_number, name=name, sex=sex, pclass_id=pclass,
                                                    nation=nation, birthday=birthday, birthplace=birthplace)
        url = reverse('student_list')
        return redirect(url)


@login_auth
def teacher_list(request):
    if request.method == 'GET':
        username = request.GET.get('username')
        teacher_list = models.Teacher.objects.all()
        return render(request, 'teacher_list.html', locals())

@login_auth
def teacher_delete(request):
    if request.method == 'GET':
        id = request.GET.get('id')
        models.Teacher.objects.get(id=id).delete()
        url = reverse('teacher_list')
        return redirect(url)

@login_auth
def teacher_add(request):
    if request.method == 'GET':
        teacher = models.Teacher.objects.all()
        return render(request, 'teacher_add.html', locals())
    else:
        name = request.POST.get('name')
        sex = request.POST.get('sex')
        title = request.POST.get('title')
        address = request.POST.get('address')
        phone = request.POST.get('phone')
        models.Teacher.objects.create(name=name, sex=sex, title=title, address=address, phone=phone)
        return redirect('/teacher_list/')

@login_auth
def teacher_update(request):
    if request.method == 'GET':
        id = request.GET.get('id')
        teacher = models.Teacher.objects.get(id=id)
        return render(request, 'teacher_update.html', locals())
    else:
        id = request.GET.get('id')
        name = request.POST.get('name')
        sex = request.POST.get('sex')
        title = request.POST.get('title')
        address = request.POST.get('address')
        phone = request.POST.get('phone')
        models.Teacher.objects.filter(id=id).update(name=name, sex=sex, title=title, address=address, phone=phone)
        url = reverse('teacher_list')
        return redirect(url)

@login_auth
def class_list(request):
    class_list = models.Professionalclass.objects.all()
    username = request.GET.get('username')
    return render(request, 'class_list.html', locals())

@login_auth
def class_delete(request):
    if request.method == 'GET':
        id = request.GET.get('id')
        models.Professionalclass.objects.get(id=id).delete()
        url = reverse('class_list')
        return redirect(url)

@login_auth
def class_add(request):
    if request.method == 'GET':
        pclass = models.Professionalclass.objects.all()
        return render(request, 'class_add.html', locals())
    else:
        name = request.POST.get('name')
        faculty = request.POST.get('faculty')
        models.Professionalclass.objects.create(name=name, faculty=faculty)
        return redirect('/class_list/')

@login_auth
def class_update(request):
    if request.method == 'GET':
        id = request.GET.get('id')
        pclass = models.Professionalclass.objects.get(id=id)
        return render(request, 'class_update.html', locals())
    else:
        id = request.GET.get('id')
        name = request.POST.get('name')
        faculty = request.POST.get('faculty')
        models.Professionalclass.objects.filter(id=id).update(name=name, faculty=faculty)
        url = reverse('class_list')
        return redirect(url)

@login_auth
def course_list(request):
    # username = request.GET.get('username')
    course_list = models.Course.objects.all()
    return render(request, 'course_list.html', locals())

@login_auth
def course_delete(request):
    if request.method == 'GET':
        id = request.GET.get('id')
        models.Course.objects.filter(id=id).delete()
        url = reverse('course_list')
        return redirect(url)

@login_auth
def course_add(request):
    if request.method == 'GET':
        # course=models.Course.objects.all()
        teacher_list = models.Teacher.objects.all()
        # students=models.Student.objects.all()
        return render(request, 'course_add.html', locals())

    else:
        name = request.POST.get('name')
        credit = request.POST.get('credit')
        teacher = request.POST.get('teacher')
        # students=request.POST.getlist('students')
        # print(students)
        course = models.Course.objects.create(name=name, credit=credit, teacher_id=teacher)
        #         # course.students.add(*students)
        return redirect('/course_list/')

@login_auth
def course_update(request):
    if request.method == 'GET':
        id = request.GET.get('id')
        course = models.Course.objects.get(id=id)
        teacher_list = models.Teacher.objects.all()
        return render(request, 'course_update.html', locals())
    else:
        id = request.GET.get('id')
        name = request.POST.get('name')
        credit = request.POST.get('credit')
        teacher = request.POST.get('teacher')
        models.Course.objects.filter(id=id).update(name=name, credit=credit, teacher_id=teacher)
        url = reverse('course_list')
        return redirect(url)

@login_auth
def grade_list(request):
    username = request.GET.get('username')
    grade_list = models.Grade.objects.get_queryset().order_by('id')
    paginator = Paginator(grade_list, 10)
    # 如果页码数多,让它显示前5,后5,中间是当前在的页码
    try:

        current_page_num = int(request.GET.get('page'))
        current_page = paginator.page(current_page_num)
        # 总页码数,大于11的时候
        if paginator.num_pages > 11:
            # 当前页码数-5大于1的时候,page_range应该是?
            if current_page_num - 5 < 1:
                page_range = range(1, 12)
            elif current_page_num + 5 > paginator.num_pages:
                #     当前页码数+5大于总页码数,总页码数往前推11个
                page_range = range(paginator.num_pages - 10, paginator.num_pages + 1)
            else:
                page_range = range(current_page_num - 5, current_page_num + 6)
        else:
            # 小于11,有多少页,就显示多少页
            page_range = paginator.page_range
    except Exception as e:
        current_page_num = 1
        current_page = paginator.page(current_page_num)
    return render(request, 'grade_list.html', locals())

@login_auth
def grade_delete(request):
    if request.method == 'GET':
        id = request.GET.get('id')
        models.Grade.objects.filter(id=id).delete()
        url = reverse('grade_list')
        return redirect(url)

@login_auth
def grade_add(request):
    if request.method == 'GET':
        course_list = models.Course.objects.all()
        return render(request, 'grade_add.html', locals())

    else:
        student_number = request.POST.get('student_number')
        student_id = models.Student.objects.filter(student_number=student_number).values('id')[0]['id']
        course = request.POST.get('course')
        grade = request.POST.get('grade')
        models.Grade.objects.create(student_id=student_id, course_id=course, grade=grade)
        return redirect('/grade_list/')

@login_auth
def grade_update(request):
    if request.method == 'GET':
        id = request.GET.get('id')
        grade = models.Grade.objects.get(id=id)
        course_list = models.Course.objects.all()
        return render(request, 'grade_update.html', locals())

    else:
        id = request.GET.get('id')
        student_number = request.POST.get('student_number')
        student_id = models.Student.objects.filter(student_number=student_number).values('id')[0]['id']
        # print(student_id)

        # course_name = request.POST.get('course_name')
        # course_id=models.Course.objects.filter(name=course_name).values('id')[0]['id']
        # print(course_id)

        course_id = request.POST.get('course_id')

        grade = request.POST.get('grade')
        models.Grade.objects.filter(id=id).update(student=student_id, course=course_id, grade=grade)
        url = reverse('grade_list')
        return redirect(url)

# ---------------------------------
@login_auth
def te_student_list(request):
    # username = request.GET.get('username')
    student_list = models.Student.objects.get_queryset().order_by('id')
    paginator = Paginator(student_list, 10)
    # 如果页码数多,让它显示前5,后5,中间是当前在的页码
    try:

        current_page_num = int(request.GET.get('page', 1))
        current_page = paginator.page(current_page_num)
        # print(current_page.object_list)
        # 总页码数,大于11的时候
        if paginator.num_pages > 11:
            # 当前页码数-5大于1的时候,page_range应该是?
            if current_page_num - 5 < 1:
                page_range = range(1, 12)
            elif current_page_num + 5 > paginator.num_pages:
                #     当前页码数+5大于总页码数,总页码数往前推11个
                page_range = range(paginator.num_pages - 10, paginator.num_pages + 1)
            else:
                page_range = range(current_page_num - 5, current_page_num + 6)
        else:

            page_range = paginator.page_range
    except Exception as e:
        current_page_num = 1
        current_page = paginator.page(current_page_num)

    return render(request, 'te_student_list.html', locals())


@login_auth
def te_course_list(request):
    course_list = models.Course.objects.all()
    return render(request, 'te_course_list.html', {'course_list': course_list})


@login_auth
def te_grade_list(request):
    teacher_id = request.user_obj.id
    print(teacher_id)
    grade_list = models.Grade.objects.filter(course__teacher=teacher_id).order_by('id')
    paginator = Paginator(grade_list, 10)
    # 如果页码数多,让它显示前5,后5,中间是当前在的页码
    try:

        current_page_num = int(request.GET.get('page'))
        current_page = paginator.page(current_page_num)
        # 总页码数,大于11的时候
        if paginator.num_pages > 11:
            # 当前页码数-5大于1的时候,page_range应该是?
            if current_page_num - 5 < 1:
                page_range = range(1, 12)
            elif current_page_num + 5 > paginator.num_pages:
                #     当前页码数+5大于总页码数,总页码数往前推11个
                page_range = range(paginator.num_pages - 10, paginator.num_pages + 1)
            else:
                page_range = range(current_page_num - 5, current_page_num + 6)
        else:
            # 小于11,有多少页,就显示多少页
            page_range = paginator.page_range
    except Exception as e:
        current_page_num = 1
        current_page = paginator.page(current_page_num)
    return render(request, 'te_grade_list.html', locals())


@login_auth
def te_grade_update(request):
    if request.method == 'GET':
        id = request.GET.get('id')
        grade = models.Grade.objects.get(id=id)
        course_list = models.Course.objects.all()
        return render(request, 'te_grade_update.html', locals())

    else:
        id = request.GET.get('id')
        student_number = request.POST.get('student_number')
        student_id = models.Student.objects.filter(student_number=student_number).values('id')[0]['id']
        course_id = request.POST.get('course_id')

        grade = request.POST.get('grade')
        models.Grade.objects.filter(id=id).update(student=student_id, course=course_id, grade=grade)
        return redirect('/te_grade_list/')


# ---------------------------------
def student_index(request):
    if request.method == 'GET':
        return render(request, 'student_index.html')

@login_auth
def st_grade_list(request):
    student_id = request.user_obj.id
    print(student_id)
    grade_list = models.Grade.objects.filter(student=student_id).order_by('id')
    paginator = Paginator(grade_list, 10)
    # 如果页码数多,让它显示前5,后5,中间是当前在的页码
    try:

        current_page_num = int(request.GET.get('page'))
        current_page = paginator.page(current_page_num)
        # 总页码数,大于11的时候
        if paginator.num_pages > 11:
            # 当前页码数-5大于1的时候,page_range应该是?
            if current_page_num - 5 < 1:
                page_range = range(1, 12)
            elif current_page_num + 5 > paginator.num_pages:
                #     当前页码数+5大于总页码数,总页码数往前推11个
                page_range = range(paginator.num_pages - 10, paginator.num_pages + 1)
            else:
                page_range = range(current_page_num - 5, current_page_num + 6)
        else:
            # 小于11,有多少页,就显示多少页
            page_range = paginator.page_range
    except Exception as e:
        current_page_num = 1
        current_page = paginator.page(current_page_num)
    return render(request, 'st_grade_list.html', locals())

@login_auth
def student_details(request):
    if request.method == 'GET':
        student_id = request.user_obj.id
        # print(student_id)
        student_list = models.Student.objects.filter(pk=student_id)
        student_details_list=models.StudentDetail.objects.filter(pk=request.user_obj.student_detail_id).first()
        # print(student_details_list)
        return render(request, 'student_details.html', locals())
    else:
        student_id = request.user_obj.id
        # print(student_id)
        political = request.POST.get('political')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        major = request.POST.get('major')
        address=request.POST.get('address')
        experience = request.POST.get('experience')
        ability = request.POST.get('ability')
        hobby = request.POST.get('hobby')

        judge=models.Student.objects.filter(pk=student_id).first()
        print(judge)
        if not judge.student_detail_id:
            student_detail = models.StudentDetail.objects.create(political=political, phone=phone, email=email, major=major,
                                                                 address=address,experience=experience, ability=ability, hobby=hobby)
            models.Student.objects.filter(pk=student_id).update(student_detail_id=student_detail.pk)
        else:
            student_detail = models.StudentDetail.objects.filter(student__id=student_id).update(political=political, phone=phone, email=email,
                                                                 major=major,
                                                                 address=address, experience=experience,
                                                               ability=ability, hobby=hobby)
            print(student_detail)
        return redirect('/student_details/')

# 已弃用
def Tableau_list(request):
    if request.method == 'GET':
        pclass_list = models.Professionalclass.objects.all()
        course_list = models.Course.objects.all()
        student_list = models.Student.objects.all()
        courses = models.Course.objects.all()

        return render(request, 'Tableau_list.html', locals())

# ---------------------------------
# 文章部分
def st_blog(request):
    name = request.GET.get('name')
    article_list = models.Article.objects.filter(student__name=name).all()
    return render(request,'blog.html',locals())


def BlogArticle(request,nid):
    name = request.GET.get('name')
    user = models.Student.objects.filter(name=name).first()
    cur_article = models.Article.objects.filter(nid=nid).first()
    if not cur_article:
        return render(request,'404.html')
    commit_list = models.Commit.objects.filter(article=cur_article).all()
    return render(request, 'blog_article.html', locals())

from django.views import View
class CommentAdd(View):
    def post(self,request):
        comment = request.POST.get('comment')
        id = request.POST.get('id')
        name = request.POST.get('name')
        commit = models.Commit.objects.create(content=comment,user=name,article_id=id)
        dic = {'status': '200'}
        return JsonResponse(dic)


class IndexBlog(View):
    def get(self, request):
        name = request.GET.get('name')
        article_list = models.Article.objects.all().order_by("-create_time")
        paginator = Paginator(article_list, 4)
        try:
            current_page_num = int(request.GET.get('page'))
            current_page = paginator.page(current_page_num)
        except Exception:
            current_page_num = 1
            current_page = paginator.page(current_page_num)
        if paginator.num_pages > 5:
            if current_page_num - 2 < 1:
                page_range = range(1, 6)
            elif current_page_num + 2 > paginator.num_pages:
                page_range = range(paginator.num_pages - 4, paginator.num_pages + 1)
            else:
                page_range = range(current_page_num - 2, current_page_num + 3)
        else:
            page_range = paginator.page_range
        return render(request, 'index_blog.html', locals())


class Backend(View):
    def get(self,request):
        name = request.GET.get('name')
        student = models.Student.objects.filter(name=name)
        article_list = models.Article.objects.filter(student=student).all()
        paginator = Paginator(article_list, 4)
        try:
            current_page_num = int(request.GET.get('page'))
            current_page = paginator.page(current_page_num)
        except Exception:
            current_page_num = 1
            current_page = paginator.page(current_page_num)
        if paginator.num_pages > 5:
            if current_page_num - 2 < 1:
                page_range = range(1, 6)
            elif current_page_num + 2 > paginator.num_pages:
                page_range = range(paginator.num_pages - 4, paginator.num_pages + 1)
            else:
                page_range = range(current_page_num - 2, current_page_num + 3)
        else:
            page_range = paginator.page_range
        return render(request, 'backend.html',locals())


class ArticleDel(View):
    def get(self,request,pk):
        name = request.GET.get('name')
        student = models.Student.objects.filter(name=name)
        models.Article.objects.filter(student=student,pk=pk).delete()
        url='/backend/?name='+name
        return redirect(url)

from bs4 import BeautifulSoup
class ArticleUpdate(View):
    def get(self,request,pk):
        name = request.GET.get('name')
        student = models.Student.objects.filter(name=name).first()
        article = models.Article.objects.filter(pk=pk).first()
        return render(request,'article_update.html',locals())

    def post(self,request,pk):
        name = request.GET.get('name')
        title = request.POST.get('title')
        content = request.POST.get('content')
        soup = BeautifulSoup(content, 'html.parser')
        tags = soup.find_all()
        for tag in tags:
            if tag.name == 'script':
                tag.decompose()
        desc = soup.text[0:150]
        models.Article.objects.filter(pk=pk).update(title=title, content=content, desc=desc)
        print('/backend/?name=' + name)
        dic = {'status': '200', 'url': '/backend/?name='+name}

        return JsonResponse(dic)


class ArticleAdd(View):

    def get(self,request):
        name = request.GET.get('name')
        return render(request, 'article_add.html',locals())

    def post(self,request):
        name = request.GET.get('name')
        student = models.Student.objects.filter(name=name).first()
        title = request.POST.get('title')
        content = request.POST.get('content')
        soup = BeautifulSoup(content, 'html.parser')
        tags = soup.find_all()
        for tag in tags:
            if tag.name == 'script':
                tag.decompose()
        desc = soup.text[0:150]
        art = models.Article.objects.create(title=title, content=content, desc=desc,student=student)
        dic = {'status': '200', 'url': '/backend/?name='+name}
        return JsonResponse(dic)

import os
from student_management_system import settings
class UploadImg(View):
    def post(self,request):
        myfile = request.FILES.get('myfile')
        path = os.path.join(settings.BASE_DIR, 'media', 'img')
        if not os.path.isdir(path):
            os.mkdir(path)
        file_path = os.path.join(path, myfile.name)
        with open(file_path, 'wb') as f:
            for line in myfile:
                f.write(line)
        dic = {'error': 0, 'url': '/media/img/%s' % myfile.name}
        return JsonResponse(dic)




# ---------------------------------
# 数据可视化部分
# 个人成绩
def index_student(request):
    from pyecharts import Bar
    student_id = request.user_obj.id

    student=models.Student.objects.filter(pk=student_id).all().first()
    student_name=student.name
    grade_list = models.Grade.objects.filter(student=student_id).all()
    ll = []
    l2 = []

    for sudentgrade in grade_list:
        # print(sudentgrade.student)
        # print(sudentgrade.grade)
        ll.append(str(sudentgrade.course.name))  # 对象类型强制转换成字符串类型
        l2.append(int(sudentgrade.grade))  # 同理
    attr = ll
    v1 = l2
    # attr = ["同学1", "同学2", "同学3"]
    # v1 = [5, 20, 36]
    bar = Bar("%s的成绩" % student_name, width=800)
    bar.add(student_name , attr, v1, mark_point=["max", "min"], mark_line=["average"])
    # attr = ["衬衫", "羊毛衫", "雪纺衫", "裤子", "高跟鞋", "袜子"]
    # v1 = [5, 20, 36, 10, 75, 90]
    # v2 = [10, 25, 8, 60, 20, 80]
    # bar = Bar("柱状图数据堆叠示例")
    # bar.add("商家A", attr, v1, is_stack=True)
    # bar.add("商家B", attr, v2, is_stack=True)
    bar.render('templates/imagelist/personal_grade.html')
    return render(request, 'imagelist/personal_grade.html')

# 男女生比例
def index(request):
    if request.method == 'GET':
        pclass_list = models.Professionalclass.objects.all()
        return render(request,'index.html',locals())
    else:
        from pyecharts import Pie
        from django.db.models import Avg, Count, Max, Min, Sum
        pclass = request.POST.get('pclass')
        # print('pclass')  1
        # pclass='20152831'
        attr = ["男生", "女生"]
        # pclass = '2'
        class_name = models.Professionalclass.objects.filter(id=pclass).first()
        # print(class_name) Professionalclass object
        cl_name = class_name.name
        # print(cl_name) 20152831
        boy_count = models.Student.objects.filter(pclass_id=pclass, sex='男').count()
        girl_count = models.Student.objects.filter(pclass_id=pclass, sex='女').count()
        v1 = [boy_count, girl_count]
        pie = Pie("%s班男女比例" % cl_name)
        pie.add("", attr, v1, is_label_show=True)
        pie.render('templates/imagelist/genderratio.html')
        return render(request, 'imagelist/genderratio.html')


# 籍贯
def index2(request):
    from pyecharts import Map
    students = models.Student.objects.all()
    ll = []
    judge = []  # 判断有无该省
    for student in students:
        dic = {"place": None, "count": 0}
        # print(student.birthplace) 浙江台州市
        if student.birthplace[0:2] not in judge:
            judge.append(student.birthplace[0:2])
            dic["place"] = student.birthplace[0:2]
            dic["count"] = 1
            ll.append(dic)
        else:
            for p in ll:
                if p["place"] == student.birthplace[0:2]:
                    p["count"] += 1
    # print(ll)
    # [{'place': '山东', 'count': 2}, {'place': '浙江', 'count': 20}, {'place': '江苏', 'count': 6},]
    val = []
    att = []
    for obj in ll:
        att.append(obj["place"])
        val.append(obj["count"])
    # print(val)
    # print(att)
    value = val
    attr = att
    # value = [155, 10, 66, 78, 33, 80, 190, 53, 49.6]
    # attr = [
    #     "福建", "山东", "北京", "上海", "甘肃", "新疆", "河南", "广西", "西藏"
    # ]
    map = Map("学生籍贯数据可视化", width=1200, height=600)
    map.add(
        "",
        attr,
        value,
        maptype="china",
        is_visualmap=True,
        visual_text_color="#000",
        visual_range=[0, 10],
    )

    map.render('templates/imagelist/birthplace.html')
    with open('templates/imagelist/birthplace.html', 'rb') as f:
        data = f.read()
    return HttpResponse(data)


# 各省学生
def index3(request):
    if request.method == 'GET':
        return render(request,'index3.html')
    else:
        from pyecharts import Map
        birthplace = request.POST.get('birthplace')
        birth_place = birthplace[0:2]
        print(birth_place)
        students = models.Student.objects.all()
        ll = []
        judge = []  # 判断有无该省
        for student in students:
            dic = {"place": None, "count": 0}
            # print(student.birthplace) 浙江台州市
            if student.birthplace[0:2] == birth_place:
                # if student.birthplace[0:2]=='浙江':
                if student.birthplace[2:] not in judge:
                    judge.append(student.birthplace[2:])
                    dic["place"] = student.birthplace[2:]
                    dic["count"] = 1
                    ll.append(dic)
                else:
                    for p in ll:
                        if p["place"] == student.birthplace[2:]:
                            p["count"] += 1
        val = []
        att = []
        for obj in ll:
            att.append(obj["place"])
            val.append(obj["count"])
        value = val
        attr = att
        map = Map("%s" % birth_place, width=1200, height=600)

        map.add("", attr, value, maptype=birth_place, visual_range=[0, 6], is_visualmap=True, visual_text_color='#000')
        # map.add("", attr, value, maptype='浙江', visual_range=[0,6], is_visualmap=True, visual_text_color='#000')
        map.render('templates/imagelist/st_province.html')
        return render(request, 'imagelist/st_province.html')


# 各班某门课程成绩
def index4(request):
    if request.method == 'GET':
        pclass_list = models.Professionalclass.objects.all()
        course_list = models.Course.objects.all()
        return render(request, 'index4.html',locals())
    else:
        from pyecharts import Bar
        course = request.POST.get('course')
        pclass = request.POST.get('pclass')
        class_name = models.Professionalclass.objects.filter(id=pclass).first()
        cl_name = class_name.name
        course_name = models.Course.objects.filter(id=course).first()
        cour_name = course_name.name
        print(cour_name)
        sudentgrades = models.Grade.objects.filter(course=course, student__pclass=pclass).all()
        ll = []
        l2 = []

        for sudentgrade in sudentgrades:
            # print(sudentgrade.student)
            # print(sudentgrade.grade)
            ll.append(str(sudentgrade.student))  # 对象类型强制转换成字符串类型
            l2.append(int(sudentgrade.grade))  # 同理
        attr = ll
        v1 = l2
        # attr = ["同学1", "同学2", "同学3"]
        # v1 = [5, 20, 36]
        bar = Bar("课程:%s" % cour_name, width=1600)
        bar.add("%s班" % cl_name, attr, v1, mark_point=["max", "min"], mark_line=["average"])

        bar.render('templates/imagelist/class_grade.html')
        return render(request, 'imagelist/class_grade.html')

# 本班科目成绩对比图
import decimal
def index5(request):
    if request.method == 'GET':
        pclass_list = models.Professionalclass.objects.all()
        course_list = models.Course.objects.all()
        return render(request, 'index5.html',locals())
    else:
        from pyecharts import Bar

        courses = request.POST.getlist('courses') #['1','2','4']
        pclass = request.POST.get('pclass')
        ll = []
        createVar = locals()
        dic={}
        list2=[]
        for course in courses:
            dic['v'+course]=course
            course_name = models.Course.objects.filter(id=course).first()
            tup1=['v'+course,course_name.name]
            list2.append(tup1)
        # print(list2)
        l2=[]
        for key,value in dic.items():
            # key=value
            l2.append(key)
        dic1={}
        for course in courses:
            for i in l2:
                if 'v'+course == i:
                    grades = models.Grade.objects.filter(course=course, student__pclass=pclass).all().values_list('grade')
                    dic1[i]=grades
        # print(dic1)
        dic3={}
        for i in l2:
            dic3[i]=[]
            for j in dic1[i]:
                j=int(j[0])
                dic3[i].append(j)

        students = models.Grade.objects.filter(student__pclass=pclass).all().values_list('student__name').distinct()
        attr=[]
        for student in students:
            attr.append(student[0])
        # print(attr)
        bar = Bar("柱状图数据堆叠示例", width=1600)
        # print(dic3)
        for i in l2:
            for j in list2:
                if j[0] ==i:
                    dic = dic3[i]
                    if len(dic3[i])!=len(attr):
                        l=[]
                        for k in range(len(attr)):
                            l.append(0)

                        for i in dic:
                            print(i)
                            names = models.Grade.objects.filter(grade=i,student__pclass=pclass,course__name=j[1]).all().values_list(
                                'student__name')


                            for name in names:
                                print(name)
                                index = attr.index(name[0])
                                print(index)
                                l[index]=i
                        print(l)
                        dic=l

                    # print(attr)
                    # print(dic)
                    print('--------start')
                    print(len(attr))        #21
                    print(len(dic))         #21
                    print('--------start')
                    bar.add(j[1], attr,dic, mark_line=["average"])

        # v1 = l2

    # ['王芳泽', '王芳泽', '王芳泽', '李晓瑶', '李晓瑶', '李晓瑶', '张凡儿', '张凡儿', '张凡儿', '刘英豪', '刘英豪', '刘英豪', '杨思萱', '杨思萱', '杨思萱', '黄建元',
    #  '黄建元', '黄建元', '周翔飞', '周翔飞', '周翔飞', '王飞燕', '王飞燕', '王飞燕', '吴明杰', '吴明杰', '吴明杰', '林强', '林强', '林强', '刘勇捷', '刘勇捷', '刘勇捷',
    #  '黄阳', '黄阳', '黄阳', '陈静逸', '陈静逸', '陈静逸', '张安怡', '张安怡', '张安怡', '刘俊名', '刘俊名', '刘俊名', '王瑶', '王瑶', '王瑶', '李宏儒', '李宏儒',
    #  '李宏儒', '朱乐欣', '朱乐欣', '朱乐欣', '李清照', '李清照', '李清照', '马逸龙', '马逸龙', '马逸龙', '林美美', '林美美', '林美美']
    # [87, 85, 85, 98, 72, 87, 87, 79, 88, 92, 90, 75, 85, 88, 89, 83, 86, 80, 81, 95, 74, 92, 90, 93, 91, 88, 80, 94, 72,
    #  70, 88, 89, 71, 93, 80, 90, 93, 83, 92, 96, 94, 93, 72, 70, 74, 99, 97, 98, 90, 92, 80, 88, 78, 60, 78, 79, 89, 87,
    #  81, 76, 82, 70, 90]

        bar.render('templates/imagelist/contrast_grade.html')
        return render(request, 'imagelist/contrast_grade.html')

# 多班级比较某课平均值
def index6(request):
    if request.method == 'GET':
        pclass_list = models.Professionalclass.objects.all()
        course_list = models.Course.objects.all()
        return render(request, 'index6.html',locals())
    else:
        from pyecharts import Bar
        course = request.POST.get('course')  # 1
        pclasses = request.POST.getlist('pclass')  # ['1','2']
        dic = {}
        list = []
        attr = []
        for pclass in pclasses:
            list.append('v' + pclass)
            p = models.Professionalclass.objects.filter(id=pclass).first()
            attr.append(p.name)
            student_id = models.Student.objects.filter(pclass_id=pclass).values_list('id')
            if not student_id:
                # return redirect('/Tableau_list/')
                return HttpResponse("请去联系管理员，确认所选每个班级都已录入学生信息！")
            l = []
            for student in student_id:
                ret = models.Grade.objects.filter(course_id=course, student_id=student).first()
                if not ret:
                    l.append(0)
                    dic['v' + pclass] = l
                else:
                    l.append(ret.grade)
                    dic['v' + pclass] = l
        # print(dic)
        bar = Bar("各班平均成绩比较", width=800)
        avg_list = []
        for i in list:
            i = dic[i]
            avg = float(sum(i) / len(i))
            avg_list.append(avg)
        c = models.Course.objects.filter(id=course).first()
        bar.add(c.name, attr, avg_list, mark_line=["average"])
        bar.render('templates/imagelist/many_contrast_grade.html')

        return render(request, 'imagelist/many_contrast_grade.html')

# X轴：学生姓名  Y轴：课程名称 Z轴：成绩
def index7(request):
    from pyecharts import Bar3D

    bar3d = Bar3D("3D 柱状图示例", width=1200, height=600)
    x_axis = [
        "12a", "1a", "2a", "3a", "4a", "5a", "6a", "7a", "8a", "9a", "10a", "11a",
        "12p", "1p", "2p", "3p", "4p", "5p", "6p", "7p", "8p", "9p", "10p", "11p"
    ]
    y_axis = [
        "Saturday", "Friday", "Thursday", "Wednesday", "Tuesday", "Monday", "Sunday"
    ]

    data = [

    ]
    data = [
        [0, 0, 5], [0, 1, 1], [0, 2, 0], [0, 3, 0], [0, 4, 0], [0, 5, 0],
        [0, 6, 0], [0, 7, 0], [0, 8, 0], [0, 9, 0], [0, 10, 0], [0, 11, 2],
        [0, 12, 4], [0, 13, 1], [0, 14, 1], [0, 15, 3], [0, 16, 4], [0, 17, 6],
        [0, 18, 4], [0, 19, 4], [0, 20, 3], [0, 21, 3], [0, 22, 2], [0, 23, 5],
        [1, 0, 7], [1, 1, 0], [1, 2, 0], [1, 3, 0], [1, 4, 0], [1, 5, 0],
        [1, 6, 0], [1, 7, 0], [1, 8, 0], [1, 9, 0], [1, 10, 5], [1, 11, 2],
        [1, 12, 2], [1, 13, 6], [1, 14, 9], [1, 15, 11], [1, 16, 6], [1, 17, 7],
        [1, 18, 8], [1, 19, 12], [1, 20, 5], [1, 21, 5], [1, 22, 7], [1, 23, 2],
        [2, 0, 1], [2, 1, 1], [2, 2, 0], [2, 3, 0], [2, 4, 0], [2, 5, 0],
        [2, 6, 0], [2, 7, 0], [2, 8, 0], [2, 9, 0], [2, 10, 3], [2, 11, 2],
        [2, 12, 1], [2, 13, 9], [2, 14, 8], [2, 15, 10], [2, 16, 6], [2, 17, 5],
        [2, 18, 5], [2, 19, 5], [2, 20, 7], [2, 21, 4], [2, 22, 2], [2, 23, 4],
        [3, 0, 7], [3, 1, 3], [3, 2, 0], [3, 3, 0], [3, 4, 0], [3, 5, 0],
        [3, 6, 0], [3, 7, 0], [3, 8, 1], [3, 9, 0], [3, 10, 5], [3, 11, 4],
        [3, 12, 7], [3, 13, 14], [3, 14, 13], [3, 15, 12], [3, 16, 9], [3, 17, 5],
        [3, 18, 5], [3, 19, 10], [3, 20, 6], [3, 21, 4], [3, 22, 4], [3, 23, 1],
        [4, 0, 1], [4, 1, 3], [4, 2, 0], [4, 3, 0], [4, 4, 0], [4, 5, 1],
        [4, 6, 0], [4, 7, 0], [4, 8, 0], [4, 9, 2], [4, 10, 4], [4, 11, 4],
        [4, 12, 2], [4, 13, 4], [4, 14, 4], [4, 15, 14], [4, 16, 12], [4, 17, 1],
        [4, 18, 8], [4, 19, 5], [4, 20, 3], [4, 21, 7], [4, 22, 3], [4, 23, 0],
        [5, 0, 2], [5, 1, 1], [5, 2, 0], [5, 3, 3], [5, 4, 0], [5, 5, 0],
        [5, 6, 0], [5, 7, 0], [5, 8, 2], [5, 9, 0], [5, 10, 4], [5, 11, 1],
        [5, 12, 5], [5, 13, 10], [5, 14, 5], [5, 15, 7], [5, 16, 11], [5, 17, 6],
        [5, 18, 0], [5, 19, 5], [5, 20, 3], [5, 21, 4], [5, 22, 2], [5, 23, 0],
        [6, 0, 1], [6, 1, 0], [6, 2, 0], [6, 3, 0], [6, 4, 0], [6, 5, 0],
        [6, 6, 0], [6, 7, 0], [6, 8, 0], [6, 9, 0], [6, 10, 1], [6, 11, 0],
        [6, 12, 2], [6, 13, 1], [6, 14, 3], [6, 15, 4], [6, 16, 0], [6, 17, 0],
        [6, 18, 0], [6, 19, 0], [6, 20, 1], [6, 21, 2], [6, 22, 2], [6, 23, 6]
    ]
    range_color = ['#313695', '#4575b4', '#74add1', '#abd9e9', '#e0f3f8', '#ffffbf',
                   '#fee090', '#fdae61', '#f46d43', '#d73027', '#a50026']
    bar3d.add(
        "",
        x_axis,
        y_axis,
        [[d[1], d[0], d[2]] for d in data],
        is_visualmap=True,
        visual_range=[0, 20],
        visual_range_color=range_color,
        grid3d_width=200,
        grid3d_depth=80,
    )

    bar3d.render('templates/imagelist/class_grade3d.html')
    with open('templates/imagelist/class_grade3d.html', 'rb') as f:
        data = f.read()
    return HttpResponse(data)

def new1(request):
    return render(request,'new1.html')



