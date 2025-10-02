from django.contrib.auth.models import User
from django.db import models


class Task(models.Model):
    # Fields
    title = models.CharField(max_length=255)
    desc = models.TextField(blank=True, null=True)  # Make desc optional

    position = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    # Choices for status
    STATUS_CHOICES = [
        ('todo', 'To Do'),
        ('progress', 'In Progress'),
        ('done', 'Done')
    ]

    status = models.CharField(
        max_length=10,  # 'todo', 'progress', or 'done' will fit here
        choices=STATUS_CHOICES,
        default='todo'
    )
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High')
    ]
    priority = models.CharField(
        max_length=6,  # 'Low', 'Medium', or 'High' will fit here
        choices=PRIORITY_CHOICES,
        default='low'  # Default to 'Medium'
    )

    tags = models.ManyToManyField('Tag', blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    assignee = models.ForeignKey(
        User,
        related_name='assigned_tasks',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    

    def __str__(self):
        return f"{self.id} - {self.title}"

    class Meta:
        ordering = ['created_at']  # Optionally, you can order by creation date


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Comment(models.Model):
    task = models.ForeignKey(
        Task, related_name="comments", on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Comment by {self.author} on {self.task}"
