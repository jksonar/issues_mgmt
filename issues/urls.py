from django.urls import path
from . import views

urlpatterns = [
    path('', views.issue_list, name='issue_list'),
    path('create/', views.issue_create, name='issue_create'),
    path('<int:pk>/', views.issue_detail, name='issue_detail'),
    path('<int:pk>/edit/', views.issue_edit, name='issue_edit'),
    path('<int:pk>/delete/', views.issue_delete, name='issue_delete'),
]