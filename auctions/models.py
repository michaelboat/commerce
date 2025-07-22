from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Category(models.Model):
    categoryName = models.CharField(max_length=50)

class Listing(models.Model):
    title = models.CharField(max_length=30)
    description = models.CharField(max_length=300)
    imageURL =  models.CharField(max_length=1000)
    price = models.FloatField()
    isAction = models.BooleanField(default=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE , blank = True, related_name="user")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True, null=True, related_name="category")
    
