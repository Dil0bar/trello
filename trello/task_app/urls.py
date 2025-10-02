from django.urls import path

from . import views
from .views import task_delete, task_detail, task_list_or_create, update_task_status

urlpatterns = [
    path('', task_list_or_create, name='task_list_or_create'),
    path('detail/<int:task_id>/', task_detail, name='task_detail'),
    path("task/<int:task_id>/edit/", views.task_edit, name="task_edit"),
    path('delete/<int:task_id>/', task_delete, name='task_delete'),
    path('update-task-status/', update_task_status, name='update_task_status'),
    path("task/<int:task_id>/comment/", views.add_comment, name="add_comment"),

    path('register/', views.register, name='register'),  # New registration path
    path('login/', views.user_login, name='login'),  # New login path
    path('logout/', views.user_logout, name='logout'),  # New logout path

]
