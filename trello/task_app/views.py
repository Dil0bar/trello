import json

from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt

from .models import Task, Comment

# CRUD

# List objects | GET


from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from django.views.decorators.http import require_POST

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
        if title:
            # при создании всегда попадает в "todo" в конец
            max_pos = Task.objects.filter(status="todo").count()
            Task.objects.create(title=title, desc=desc, status="todo", position=max_pos)

        return redirect('task_list_or_create')
    
    #     Task.objects.create(title=title, desc=desc)
    #     return redirect('task_list_or_create')

    tasks = Task.objects.all().order_by("position")
    return render(request, 'task_list.html', {'tasks': tasks})
    # tasks = Task.objects.all().order_by('-id')
    # return render(request, 'task_list.html', {'tasks': tasks})


def task_detail(request, task_id):
    task = Task.objects.get(id=task_id)
    return render(request, 'task_detail.html', {'task': task})


def task_delete(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    task.delete()
    return redirect('task_list_or_create')



@csrf_exempt
def update_task_status(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        task_id = data.get('task_id')
        new_status = data.get('new_status')
        order = data.get("order", [])

        # Print task_id and new_status for debugging
        print(f"Task ID: {task_id}, New Status: {new_status}")

        # Update the task's status
        try:
            task = Task.objects.get(id=task_id)
            task.status = new_status
            task.save()

             # обновляем порядок в колонке
            for item in order:
                Task.objects.filter(id=item["id"]).update(position=item["position"])

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
    #         return JsonResponse({"message": "Task status updated successfully!"}, status=200)
    #     except Task.DoesNotExist:
    #         return JsonResponse({"error": "Task not found!"}, status=404)
    # return JsonResponse({"error": "Invalid request!"}, status=400)


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

    comment = Comment.objects.create(task=task, author=request.user, text=text)
    return JsonResponse({
        "id": comment.id,
        "author": comment.author.username,
        "text": comment.text,
        "created_at": comment.created_at.strftime("%Y-%m-%d %H:%M"),
    })
