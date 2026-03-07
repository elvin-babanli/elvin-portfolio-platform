from django.db import models
from django.contrib.auth.models import User


class TodoList(models.Model):
    """User's list (Personal, Work, etc.)"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="todo_lists")
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=20, default="#6366f1")

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Tag(models.Model):
    """User's tag"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="todo_tags")
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=20, default="#06b6d4")

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Task(models.Model):
    """Main task model."""

    PRIORITY_LOW = 0
    PRIORITY_MEDIUM = 1
    PRIORITY_HIGH = 2
    PRIORITY_CHOICES = [
        (PRIORITY_LOW, "Low"),
        (PRIORITY_MEDIUM, "Medium"),
        (PRIORITY_HIGH, "High"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    due_date = models.DateField(null=True, blank=True)
    completed = models.BooleanField(default=False)
    priority = models.PositiveSmallIntegerField(
        choices=PRIORITY_CHOICES, default=PRIORITY_MEDIUM
    )
    list = models.ForeignKey(TodoList, on_delete=models.SET_NULL, null=True, blank=True, related_name="tasks")
    tags = models.ManyToManyField(Tag, blank=True, related_name="tasks")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-due_date", "-created_at"]

    def __str__(self):
        return self.title

    @property
    def subtask_count(self):
        return self.subtasks.count()

    @property
    def completed_subtask_count(self):
        return self.subtasks.filter(completed=True).count()


class Subtask(models.Model):
    """Alt görev"""
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="subtasks")
    title = models.CharField(max_length=255)
    completed = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.title
