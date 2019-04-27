from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

# class UserInfo(AbstractUser):


class Student(models.Model):
    id=models.AutoField(primary_key=True)
    student_number=models.CharField(max_length=32)
    name = models.CharField(max_length=32)
    sex = models.CharField(max_length=32)
    pclass=models.ForeignKey(to='Professionalclass',to_field='id',on_delete=models.SET_NULL,null=True)
    nation=models.CharField(max_length=32)
    birthday=models.DateField(null=True)
    birthplace=models.CharField(max_length=32)
    student_detail = models.OneToOneField(to='StudentDetail', to_field='id', null=True,on_delete=models.CASCADE)
    password=models.CharField(max_length=32,default='123')
    def __str__(self):
        return self.name

class StudentDetail(models.Model):
    id = models.AutoField(primary_key=True)
    major=models.CharField(max_length=32)
    en_time=models.DateField(null=True)
    political=models.CharField(max_length=32)
    edu_ba=models.CharField(max_length=32,default='本科')
    address = models.CharField(max_length=64)
    phone = models.CharField(max_length=32)
    email = models.EmailField()
    experience = models.TextField(null=True)
    ability = models.TextField(null=True)
    hobby = models.TextField(null=True)



class Teacher(models.Model):
    id = models.AutoField(primary_key=True)
    teacher_number = models.CharField(max_length=32,null=True)
    name = models.CharField(max_length=32)
    sex = models.CharField(max_length=32)
    title=models.CharField(max_length=32)
    address = models.CharField(max_length=64)
    phone = models.CharField(max_length=32)
    password=models.CharField(max_length=32,default='123')
    def __str__(self):
        return self.name

class Professionalclass(models.Model):
    id= models.AutoField(primary_key=True)
    name=models.CharField(max_length=32)
    faculty=models.CharField(max_length=32,null=True)


class Course(models.Model):
    id = models.AutoField(primary_key=True)
    name=models.CharField(max_length=32)
    credit=models.CharField(max_length=32)
    teacher=models.ForeignKey(to='Teacher',to_field='id',on_delete=models.CASCADE)
    students=models.ManyToManyField(to='Student',through='Grade',through_fields=('course','student'))


class Grade(models.Model):
    id = models.AutoField(primary_key=True)
    student = models.ForeignKey(to='Student', to_field='id',on_delete=models.CASCADE)
    course= models.ForeignKey(to='Course', to_field='id',on_delete=models.CASCADE)
    grade=models.DecimalField(max_digits=4,decimal_places=1)

class SuperUser(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=32)
    password= models.CharField(max_length=32,default='123')
    def __str__(self):
        return self.name


class Article(models.Model):
    nid = models.AutoField(primary_key=True)
    title = models.CharField(max_length=64)
    desc = models.CharField(max_length=255)
    content = models.TextField()
    create_time = models.DateTimeField(auto_now_add=True)
    student = models.ForeignKey(to='Student', to_field='id', null=True)


class Commit(models.Model):
    nid = models.AutoField(primary_key=True)
    user = models.CharField(max_length=255)
    article = models.ForeignKey(to='Article', to_field='nid')
    content = models.CharField(max_length=255)
    create_time = models.DateTimeField(auto_now_add=True)


