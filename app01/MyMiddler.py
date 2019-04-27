from django.utils.deprecation import MiddlewareMixin
from app01 import models
from django.shortcuts import HttpResponse, render, redirect

from app01 import models
class MyMd1(MiddlewareMixin):
    def process_request(self, request):
        # username=request.GET.get('username')
        # request.username=username


        if not request.path in ['/login/','/home/']:
            user_id = request.session.get('userid')
            if not user_id:
                return redirect('/login/')
            else:
                user_type=request.session.get('user_type')
                if user_type=='admin':
                    user_obj=models.SuperUser.objects.get(pk=user_id)
                    print(user_obj)
                elif user_type=='teacher':
                    user_obj = models.Teacher.objects.get(pk=user_id)
                else:
                    user_obj=models.Student.objects.get(pk=user_id)
                request.user_obj=user_obj
