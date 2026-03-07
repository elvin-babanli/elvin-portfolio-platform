from django.contrib import admin
from .models import Task, TodoList, Tag, Subtask


@admin.register(TodoList)
class TodoListAdmin(admin.ModelAdmin):
    list_display = ("name", "color")


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "color")


class SubtaskInline(admin.TabularInline):
    model = Subtask
    extra = 0


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("title", "list", "due_date", "completed", "created_at")
    list_filter = ("completed", "list")
    search_fields = ("title", "description")
    inlines = [SubtaskInline]
    filter_horizontal = ("tags",)
