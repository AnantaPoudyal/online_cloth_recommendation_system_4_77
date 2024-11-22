from django.contrib import admin
from .models import MasterCategory, SubCategory, ArticleType, BaseColour, Season, Gender, Products, ProductAllTags
from django.utils.html import format_html

class MasterCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'master_category_name')

class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'sub_category_name')

class ArticleTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'articleType_name')

class BaseColourAdmin(admin.ModelAdmin):
    list_display = ('id', 'baseColour_name')

class SeasonAdmin(admin.ModelAdmin):
    list_display = ('id', 'season_name')

class GenderAdmin(admin.ModelAdmin):
    list_display = ('id', 'gender_name')

class ProductsAdmin(admin.ModelAdmin):
    list_display = (
        'product_id', 'gender', 'masterCategory', 'subCategory', 'articleType',
        'baseColour', 'season', 'year', 'usage', 'productDisplayName',
        'price', 'imageName', 'image_preview', 'quantity'
    )
    search_fields = ('product_id', 'productDisplayName', 'usage', 'price', 'baseColour__baseColour_name', 'season__season_name')
    # Add search functionality on these fields. You can use __ for relationships.
    
    def image_preview(self, obj):
        if obj.imageName:
            return format_html('<img src="{}" width="50" height="50" />', obj.imageName.url)
        return "No Image"

    image_preview.short_description = 'Image'

class universalTagAdmin(admin.ModelAdmin):
    list_display = ('id', 'product_id_id', "tag_name")

class ProductPriceAdmin(admin.ModelAdmin):
    list_display = ('product_id', 'price')

# Register models with the admin site
admin.site.register(MasterCategory, MasterCategoryAdmin)
admin.site.register(SubCategory, SubCategoryAdmin)
admin.site.register(ArticleType, ArticleTypeAdmin)
admin.site.register(BaseColour, BaseColourAdmin)
admin.site.register(Season, SeasonAdmin)
admin.site.register(Gender, GenderAdmin)
admin.site.register(Products, ProductsAdmin)

admin.site.register(ProductAllTags, universalTagAdmin)
