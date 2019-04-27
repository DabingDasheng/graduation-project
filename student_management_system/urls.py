"""student_management_system URL Configuration

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
from django.conf.urls import url,include
from django.contrib import admin
from student_management_system import settings
from django.views.static import serve
from app01 import views

urlpatterns = [
    url(r'media/(?P<path>.*)$',serve,{'document_root':settings.MEDIA_ROOT}),
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.home),
    url(r'^home/$', views.home),
    url(r'^login/', views.Login.as_view()),
    url(r'^logout/', views.logout),
    url(r'^update_password/$', views.update_password),

    url(r'^index/$', views.index),
    url(r'^index2/$', views.index2),
    url(r'^index3/$', views.index3),
    url(r'^index4/$', views.index4),
    url(r'^index5/$', views.index5),
    url(r'^index6/$', views.index6),
    url(r'^index7/$', views.index7),
    url(r'^Tableau_list/$', views.Tableau_list),

    url(r'^student_list/$', views.student_list,name='student_list'),
    url(r'^student_delete/$', views.student_delete),
    url(r'^student_add/$', views.student_add),
    url(r'^student_update/$', views.student_update),
    url(r'^teacher_list/$', views.teacher_list,name='teacher_list'),
    url(r'^teacher_add/$', views.teacher_add),
    url(r'^teacher_delete/$', views.teacher_delete),
    url(r'^teacher_update/$', views.teacher_update),
    url(r'^class_list/$', views.class_list, name='class_list'),
    url(r'^class_delete/$', views.class_delete),
    url(r'^class_add/$', views.class_add),
    url(r'^class_update/$', views.class_update),
    url(r'^course_list/$', views.course_list, name='course_list'),
    url(r'^course_delete/$', views.course_delete),
    url(r'^course_add/$', views.course_add),
    url(r'^course_update/$', views.course_update),
    url(r'^grade_list/$', views.grade_list, name='grade_list'),
    url(r'^grade_delete/$', views.grade_delete),
    url(r'^grade_add/$', views.grade_add),
    url(r'^grade_update/$', views.grade_update),

    url(r'^te_student_list/$',views.te_student_list),
    url(r'^te_grade_list/$', views.te_grade_list),
    url(r'^te_course_list/$',views.te_course_list),
    url(r'^te_grade_update/$',views.te_grade_update),
    url(r'^new1/$', views.new1),

    url(r'^student_index/$', views.student_index),
    url(r'^st_grade_list/$', views.st_grade_list),
    url(r'^student_details/$', views.student_details),
    url(r'^index_student/$', views.index_student),
    url(r'^st_blog/',views.st_blog),
    url(r'^backend/',views.Backend.as_view(),name='backend'),
    url(r'^index_blog/', views.IndexBlog.as_view(), name='index_blog'),


    url(r'^comment_add/', views.CommentAdd.as_view(), name='comment_add'),
    url(r'^upload_img/', views.UploadImg.as_view()),
    url(r'^article_add/',views.ArticleAdd.as_view(),name='article_add'),
    url(r'^article_update/(?P<pk>.+).html',views.ArticleUpdate.as_view(),name='article_update'),
    url(r'^article_del/(?P<pk>.+)', views.ArticleDel.as_view(), name='article_del'),
    url(r'^article/(\d+).html', views.BlogArticle),

]
