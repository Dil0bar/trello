from django.contrib import admin

# Register your models here
from .models import Comment, Tag, Task

admin.site.register(Task)
admin.site.register(Comment)
admin.site.register(Tag)