"""
URL configuration for online_cloth_recommendation_system_4_77 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include
from user import views

urlpatterns = [

    # User pages
    path('', views.userHomepage, name='userHomepage'),
    path('items/', views.userItems, name='userItems'),
    path('itemDetail/<int:item_id>/', views.userItemDetails, name='userItemDetails'),
    path('cart/', views.userCart, name='userCart'),
    # path for 'search/
    path('search/', views.searched_items, name='user_searched_items'),
    path('dashboard/', views.dashboard, name='dashboard'),
    # path('dashboard/', views.userDashboard, name='userDashboard'),

    # Product filters by subcategory, article type, base color, season, and gender
    path('subcategory/<str:sub_category_name>/', views.user_products_by_subcategory, name='user_products_by_subcategory'),
    path('articletype/<str:articleType_name>/', views.user_products_by_article_type, name='user_products_by_article_type'),
    path('basecolour/<str:baseColour_name>/', views.user_products_by_base_colour, name='user_products_by_base_colour'),
    path('season/<str:season_name>/', views.user_products_by_season, name='user_products_by_season'),
    path('gender/<str:gender_name>/', views.user_products_by_gender, name='user_products_by_gender'),

    # Other paths can be added as needed, e.g., for user authentication, etc.


    path('account/', views.userAccount, name='userAccount'),
    path('account/update',views.updateUserAccount,name="updateUserAccount"),
    path('userCart/', views.userCart, name='userCart'),
    path('remove_from_cart/<int:product_id>/', views.remove_from_cart, name='removeFromCart'),
    path('account/edit/', views.editUserAccount, name='editUserAccount'),


    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='addToCart'),
     path('buy/<int:item_id>/', views.buy, name='buy'),
    path('purchase_success', views.purchase_success, name='purchase_success'), 
path('order_history/', views.order_history, name='userHistory'), 
 path('cancel/<int:order_id>/', views.cancel_order, name='cancel_order'),
    path('order', views.order, name='userOrder'),



    path('similar/',views.find_similar_items_for_purchased_items,name='find_similar_items'),
    path('popular/',views.popular_items_view,name='popularItem'),
   
    # path('remove-from-cart/<int:cart_item_id>/', views.remove_from_cart, name='removeFromCart'),
    path('logout', views.logout, name='logout'),

]
