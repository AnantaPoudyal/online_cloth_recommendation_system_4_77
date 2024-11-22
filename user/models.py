from django.db import models

# from manageProducts.models import Products
from manageProducts.models import Products
from viewer.models import create_user

# Create your models here.
class Cart(models.Model):
    user = models.ForeignKey(create_user, on_delete=models.CASCADE)
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.user.usernames} - {self.product.productDisplayName}"
    


class popoularItemByView(models.Model):
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    counter=models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return f"{self.product.productDisplayName} - {self.counter}"
    
class buyProduct(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('done', 'Done'),
        ('canceled', 'Canceled'),
    ]
    user = models.ForeignKey(create_user, on_delete=models.CASCADE)
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    amt = models.PositiveIntegerField(default=0)
    total=models.PositiveIntegerField()
    purchase_date = models.DateTimeField()
    address=models.CharField(max_length=255)
    contact=models.CharField(max_length=15)
    status=models.CharField(max_length=255, choices=STATUS_CHOICES,default='pending')
    
    def __str__(self):
        return f"{self.user.usernames} - {self.product.productDisplayName}"