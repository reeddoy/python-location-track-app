from django.db import models
from django.contrib.auth.models import User




# Create your models here.
class Project(models.Model):
    name = models.CharField(max_length=200, blank=True, null=True)
    lat = models.CharField(max_length=200, blank=True, null=True)
    lon = models.CharField(max_length=200, blank=True, null=True)
    radious = models.CharField(max_length=200, blank=True, null=True)
    details = models.TextField(blank=True,null=True)
    def __str__(self):
        return self.name
    


class Userprofile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    number = models.CharField(max_length=50, blank=True, null=True)
    def __str__(self):
        return self.number
    


class Add_Project_User(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project_name = models.CharField(max_length=200, blank=True, null=True)
    def __str__(self):
        return self.project_name