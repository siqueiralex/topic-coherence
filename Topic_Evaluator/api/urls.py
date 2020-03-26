from django.urls import path, include
from api import views

urlpatterns = [
    path('topic/', views.topic),
    path('model/', views.model),
]
