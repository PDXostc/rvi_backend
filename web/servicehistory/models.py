from django.contrib.auth.models import User
from django.db import models

# Create your models here.

'''
class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')


class Choice(models.Model):
    vehicle = models.ForeignKey('vehicles.Vehicle')
    user = models.ForeignKey(User)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)
'''