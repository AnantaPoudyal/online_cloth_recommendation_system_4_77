"""
URL configuration for online_cloth_recommendation_system_4_77 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from. import views

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('items/', views.items, name='items'),
    path('search_item/', views.searched_items, name='searched_items'),

    path('itemDetail/<int:item_id>/', views.itemDetails, name='itemDetail'),
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('registration_success/', views.registration_success, name='registration_success'),
    path('slider/', views.slider_view, name='slider'),



    path('subcategory/<str:sub_category_name>/', views.products_by_subcategory, name='products_by_subcategory'),
    path('articletype/<str:articleType_name>/', views.products_by_article_type, name='products_by_article_type'),
    path('basecolour/<str:baseColour_name>/', views.products_by_base_colour, name='products_by_base_colour'),
    path('season/<str:season_name>/', views.products_by_season, name='products_by_season'),
    path('gender/<str:gender_name>/', views.products_by_gender, name='products_by_gender'),


    path('forgot_password/', views.forgot_password, name='forgot_password'),
    path('password_change_sucessful', views.password_change_successful, name='password_change_sucessful'),


    
]
handler404 = 'viewer.views.custom_404_view'