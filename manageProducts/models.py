from django.db import models

# Create your models here.
class MasterCategory(models.Model):
    id = models.IntegerField(unique=True, null=True)
    master_category_name = models.CharField(max_length=255, primary_key=True)

    def __str__(self):
        return self.master_category_name

class SubCategory(models.Model):
    id = models.IntegerField(unique=True, null=True)
    sub_category_name = models.CharField(max_length=255, primary_key=True)

    def __str__(self):
        return self.sub_category_name

class ArticleType(models.Model):
    id = models.IntegerField(unique=True, null=True)
    articleType_name = models.CharField(max_length=255, primary_key=True)

    def __str__(self):
        return self.articleType_name

class BaseColour(models.Model):
    id = models.IntegerField(unique=True, null=True)
    baseColour_name = models.CharField(max_length=255, primary_key=True)

    def __str__(self):
        return self.baseColour_name

class Season(models.Model):
    id = models.IntegerField(unique=True, null=True)
    season_name = models.CharField(max_length=255, primary_key=True)

    def __str__(self):
        return self.season_name

class Gender(models.Model):
    id = models.IntegerField(unique=True, null=True)
    gender_name = models.CharField(max_length=25, primary_key=True)

    def __str__(self):
        return self.gender_name
    
class Products(models.Model):
    product_id = models.IntegerField(primary_key=True)  # Set product_id as the primary key
    gender = models.ForeignKey(Gender, on_delete=models.CASCADE)
    masterCategory = models.ForeignKey(MasterCategory, on_delete=models.CASCADE)
    subCategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE)
    articleType = models.ForeignKey(ArticleType, on_delete=models.CASCADE)
    baseColour = models.ForeignKey(BaseColour, on_delete=models.CASCADE)
    season = models.ForeignKey(Season, on_delete=models.CASCADE)
    year = models.PositiveIntegerField()
    usage = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Add price field
    productDisplayName = models.CharField(max_length=255)
    imageName = models.ImageField(upload_to='images/', blank=True, null=True)
    quantity = models.IntegerField(default=0)

    def __str__(self):
        return self.productDisplayName
    
class ProductAllTags(models.Model):
    product_id = models.ForeignKey(Products, on_delete=models.CASCADE)
    tag_name = models.CharField(max_length=255)

    def __str__(self):
        return self.tag_name