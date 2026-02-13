from django.urls import path

from . import views

urlpatterns = [
    path('products/', views.products_list, name='products_list'),
    path('types/', views.types_list, name='types_list'),
    path('brands/', views.brands_list, name='brands_list'),
    path('models/', views.models_list, name='models_list'),
    path('price-trend/', views.price_trend, name='price_trend'),
    path('policies/', views.policies_list, name='policies_list'),
    path('policies/<int:policy_id>/', views.policy_detail, name='policy_detail'),
    path('ai-chat/', views.ai_chat, name='ai_chat'),
]
