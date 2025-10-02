from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
import json

# CRUD
# List objects | GET
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .models import Comment, Task


# Детали таска + комментарии
@login_required
def task_detail(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    comments = task.comments.all()

    if request.method == "POST":
        text = request.POST.get("text")
        if text.strip():
            Comment.objects.create(task=task, author=request.user, text=text)
            return redirect("task_detail", task_id=task.id)

    return render(request, "task_detail.html", {"task": task, "comments": comments})


# Редактирование таска
@login_required
def task_edit(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    if request.method == "POST":
        task.title = request.POST.get("title")
        task.desc = request.POST.get("description")
        task.save()
        return redirect("task_detail", task_id=task.id)

    return render(request, "task_edit.html", {"task": task})


# Удаление таска
@login_required
def task_delete(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    task.delete()
    return redirect("task_list_or_create")

# Post Create Object | POST


def task_list_or_create(request):
    print(request.POST)
    if request.method == 'POST':
        title = request.POST.get('title')
        desc = request.POST.get("description")
        user = request.user
        if title:
            # при создании всегда попадает в "todo" в конец
            max_pos = Task.objects.filter(owner=user, status="todo").count()
            Task.objects.create(title=title, desc=desc,
                                status="todo", position=max_pos, owner=user)

        return redirect('task_list_or_create')

    #     Task.objects.create(title=title, desc=desc)
    #     return redirect('task_list_or_create')
    # if request.user.is_authenticated:
    tasks = Task.objects.filter(owner=request.user).order_by("position")
    # tasks = Task.objects.all().order_by("position")
    return render(request, 'task_list.html', {'tasks': tasks})
    # tasks = Task.objects.all().order_by('-id')
    # return render(request, 'task_list.html', {'tasks': tasks})


def task_detail(request, task_id):
    task = Task.objects.get(id=task_id)
    return render(request, 'task_detail.html', {'task': task, 'comments': task.comments.all()})


def task_delete(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    if task.owner != request.user:
        return HttpResponse("You are not authorized to delete this task.", status=403)
    task.delete()
    return redirect('task_list_or_create')


@csrf_exempt
def update_task_status(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        task_id = data.get('task_id')
        new_status = data.get('new_status')
        order = data.get("order", [])

        try:
            # обновляем статус задачи
            task = Task.objects.get(id=task_id)
            task.status = new_status
            task.save()

            # обновляем позиции задач в колонке
            for item in order:
                Task.objects.filter(id=item["id"]).update(
                    position=item["position"])

            return JsonResponse({
                "message": "Task status & order updated!",
                "task": {
                    "id": task.id,
                    "title": task.title,
                    "desc": task.desc,
                    "status": task.status,
                    "position": task.position
                }
            }, status=200)

        except Task.DoesNotExist:
            return JsonResponse({"error": "Task not found!"}, status=404)

    return JsonResponse({"error": "Invalid request!"}, status=400)


@csrf_exempt
@require_POST
def add_comment(request, task_id):
    try:
        task = Task.objects.get(id=task_id)
    except Task.DoesNotExist:
        return JsonResponse({"error": "Task not found"}, status=404)

    data = json.loads(request.body)
    text = data.get("text", "").strip()
    if not text:
        return JsonResponse({"error": "Empty comment"}, status=400)
    print(task_id, data)
    comment = Comment.objects.create(task=task, author=request.user, text=text)
    print(comment)
    return JsonResponse({
        "id": comment.id,
        "author": comment.author.username,
        "text": comment.text,
        "created_at": comment.created_at.strftime("%Y-%m-%d %H:%M"),
    })

from django import forms
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

#     username = forms.CharField(max_length=150)
#     email = forms.EmailField(required=False)
#     password = forms.CharField(widget=forms.PasswordInput)
#     password2 = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")


def register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        password2 = request.POST.get("password2")

        if len(username) < 3:
            return render(request, "register.html", {"error": "Username must be at least 3 characters long."})

        if len(password) < 6:
            return render(request, "register.html", {"error": "Password must be at least 6 characters long."})

        if password != password2:
            return render(request, "register.html", {"error": "Passwords do not match."})

        if username and password:
            try:
                User.objects.get(username=username)
                return render(request, "register.html", {"error": "Username already exists."})
            except User.DoesNotExist:
                User.objects.create_user(
                    username=username, password=password, email=email)
                return redirect("login")
        else:
            return render(request, "register.html", {"error": "Please provide both username and password."})

    return render(request, "register.html")


def user_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("task_list_or_create")
        else:
            return render(request, "login.html", {"error": "Invalid credentials."})

    return render(request, "login.html")


def user_logout(request):
    logout(request)
    return redirect("login")
