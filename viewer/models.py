from django.db import models

# Create your models here.

class create_user(models.Model):
    usernames = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    DOB = models.DateField()
    address = models.CharField(max_length=255)


    
