from django.contrib import admin
from app01 import models
# Register your models here.
admin.site.register(models.Student)
admin.site.register(models.StudentDetail)
admin.site.register(models.Teacher)
admin.site.register(models.Professionalclass)
admin.site.register(models.Course)
admin.site.register(models.Grade)
