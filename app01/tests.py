from django.test import TestCase

# Create your tests here.
import os
if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "student_management_system.settings")
    import django
    django.setup()
from  app01 import models
from django.db.models import Avg, Count, Max, Min, Sum

pclass='1'
boy_count=models.Student.objects.filter(pclass_id=pclass,sex='男').count()
# girl_count=models.Student.objects.filter(pclass_id=pclass,sex='女').count()

# queryResult = Book.objects.filter(title__startswith="Py").annotate(num_authors=Count('authors'))/
print(boy_count)