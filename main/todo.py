"""
Todo app: views and API for task/list/tag/subtask CRUD.
Modern, professional task management with search, sort, filters, and priority.
Authentication required; all data is scoped to the current user.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Max, Q
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from .models import Task, TodoList, Tag, Subtask


def _get_tasks_for_view(
    user,
    filter_type="all",
    list_id=None,
    tag_id=None,
    completed_filter=None,
    search_q=None,
    sort_by="date",
):
    """Filter and sort tasks by view type, search, and sort options. User-scoped."""
    today = timezone.now().date()
    tasks = (
        Task.objects.filter(user=user)
        .select_related("list")
        .prefetch_related("tags", "subtasks")
    )

    if filter_type == "today":
        tasks = tasks.filter(due_date=today)
    elif filter_type == "upcoming":
        tasks = tasks.filter(due_date__gte=today)
    elif filter_type == "overdue":
        tasks = tasks.filter(due_date__lt=today, completed=False)
    elif filter_type == "list" and list_id:
        tasks = tasks.filter(list_id=list_id)
    elif filter_type == "tag" and tag_id:
        tasks = tasks.filter(tags__id=tag_id).distinct()

    if completed_filter == "completed":
        tasks = tasks.filter(completed=True)
    elif completed_filter == "pending":
        tasks = tasks.filter(completed=False)

    if search_q and search_q.strip():
        q = search_q.strip()
        tasks = tasks.filter(
            Q(title__icontains=q)
            | Q(description__icontains=q)
            | Q(tags__name__icontains=q)
            | Q(list__name__icontains=q)
        ).distinct()

    if sort_by == "priority":
        tasks = tasks.order_by("-priority", "-due_date", "-created_at")
    elif sort_by == "priority_asc":
        tasks = tasks.order_by("priority", "-due_date", "-created_at")
    elif sort_by == "date":
        tasks = tasks.order_by("-due_date", "-created_at")
    elif sort_by == "date_asc":
        tasks = tasks.order_by("due_date", "created_at")
    elif sort_by == "alpha":
        tasks = tasks.order_by("title")
    elif sort_by == "alpha_desc":
        tasks = tasks.order_by("-title")
    else:
        tasks = tasks.order_by("-due_date", "-created_at")

    return tasks


@login_required
def todo_page(request):
    """Main todo page: dashboard with sidebar, task list, and detail panel."""
    user = request.user
    filter_type = request.GET.get("filter", "all")
    list_id = request.GET.get("list_id")
    tag_id = request.GET.get("tag_id")
    task_id = request.GET.get("task_id")
    completed_filter = request.GET.get("completed")  # completed, pending, or None
    search_q = request.GET.get("q", "")
    sort_by = request.GET.get("sort", "date")

    list_id_int = int(list_id) if list_id and str(list_id).isdigit() else None
    tag_id_int = int(tag_id) if tag_id and str(tag_id).isdigit() else None

    tasks = _get_tasks_for_view(
        user, filter_type, list_id_int, tag_id_int, completed_filter, search_q, sort_by
    )
    lists = TodoList.objects.filter(user=user)
    lists_with_counts = [
        {"list": lst, "count": Task.objects.filter(user=user, list=lst).count()}
        for lst in lists
    ]
    tags = Tag.objects.filter(user=user)
    tags_with_counts = [
        {"tag": t, "count": Task.objects.filter(user=user, tags=t).count()} for t in tags
    ]

    selected_task = None
    if task_id:
        selected_task = get_object_or_404(
            Task.objects.filter(user=user).prefetch_related("subtasks", "tags"),
            id=task_id,
        )

    today = timezone.now().date()
    user_tasks = Task.objects.filter(user=user)
    total_tasks = user_tasks.count()
    completed_count = user_tasks.filter(completed=True).count()
    pending_count = total_tasks - completed_count
    upcoming_count = user_tasks.filter(due_date__gte=today).count()
    today_count = user_tasks.filter(due_date=today).count()
    overdue_count = user_tasks.filter(due_date__lt=today, completed=False).count()

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "create_task":
            title = request.POST.get("title", "").strip()
            if title:
                due = request.POST.get("due_date") or None
                list_pk = request.POST.get("list_id") or None
                priority = request.POST.get("priority")
                try:
                    priority = int(priority) if priority else Task.PRIORITY_MEDIUM
                except (ValueError, TypeError):
                    priority = Task.PRIORITY_MEDIUM
                list_pk = list_pk if list_pk and TodoList.objects.filter(user=user, id=list_pk).exists() else None
                task = Task.objects.create(
                    user=user,
                    title=title,
                    due_date=due or None,
                    list_id=list_pk or None,
                    priority=priority,
                )
                params = f"filter={filter_type}&task_id={task.id}&created=1"
                if list_id:
                    params += f"&list_id={list_id}"
                if tag_id:
                    params += f"&tag_id={tag_id}"
                if completed_filter:
                    params += f"&completed={completed_filter}"
                if search_q:
                    params += f"&q={search_q}"
                if sort_by != "date":
                    params += f"&sort={sort_by}"
                return redirect(
                    request.get_full_path().split("?")[0] + "?" + params
                )
        elif action == "update_task":
            pk = request.POST.get("task_id")
            task = get_object_or_404(Task, id=pk, user=user)
            task.title = request.POST.get("title", task.title).strip() or task.title
            task.description = request.POST.get("description", task.description)
            task.completed = request.POST.get("completed") == "on"
            raw_due = request.POST.get("due_date")
            task.due_date = raw_due if raw_due else None
            list_pk = request.POST.get("list_id")
            task.list_id = list_pk if list_pk and TodoList.objects.filter(user=user, id=list_pk).exists() else None
            priority = request.POST.get("priority")
            if priority is not None and priority != "":
                try:
                    task.priority = int(priority)
                except (ValueError, TypeError):
                    pass
            tag_ids = request.POST.getlist("tags")
            task.tags.set(Tag.objects.filter(id__in=tag_ids, user=user))
            task.save()
            url = request.get_full_path()
            if "?" in url:
                url += "&updated=1"
            else:
                url += "?updated=1"
            return redirect(url)
        elif action == "delete_task":
            pk = request.POST.get("task_id")
            task = get_object_or_404(Task, id=pk, user=user)
            task.delete()
            base = request.get_full_path().split("?")[0]
            qs = f"?filter={filter_type}&deleted=1"
            if list_id:
                qs += f"&list_id={list_id}"
            if tag_id:
                qs += f"&tag_id={tag_id}"
            if completed_filter:
                qs += f"&completed={completed_filter}"
            if search_q:
                qs += f"&q={search_q}"
            if sort_by != "date":
                qs += f"&sort={sort_by}"
            return redirect(base + qs)
        elif action == "toggle_task":
            pk = request.POST.get("task_id")
            task = get_object_or_404(Task, id=pk, user=user)
            task.completed = not task.completed
            task.save()
            return redirect(request.get_full_path())
        elif action == "create_list":
            name = request.POST.get("list_name", "").strip()
            if name:
                color = request.POST.get("list_color", "#6366f1")
                TodoList.objects.create(user=user, name=name, color=color)
            return redirect(request.get_full_path())
        elif action == "create_tag":
            name = request.POST.get("tag_name", "").strip()
            if name:
                color = request.POST.get("tag_color", "#06b6d4")
                Tag.objects.create(user=user, name=name, color=color)
            return redirect(request.get_full_path())
        elif action == "create_subtask":
            pk = request.POST.get("task_id")
            task = get_object_or_404(Task, id=pk, user=user)
            st_title = request.POST.get("subtask_title", "").strip() or "Subtask"
            max_order = task.subtasks.aggregate(max_o=Max("order"))["max_o"] or 0
            Subtask.objects.create(task=task, title=st_title, order=max_order + 1)
            q = f"?filter={filter_type}&task_id={pk}"
            if list_id_int:
                q += f"&list_id={list_id_int}"
            if tag_id_int:
                q += f"&tag_id={tag_id_int}"
            if completed_filter:
                q += f"&completed={completed_filter}"
            if search_q:
                q += f"&q={search_q}"
            if sort_by != "date":
                q += f"&sort={sort_by}"
            return redirect(request.path + q)
        elif action == "toggle_subtask":
            st_id = request.POST.get("subtask_id")
            st = get_object_or_404(Subtask, id=st_id, task__user=user)
            st.completed = not st.completed
            st.save()
            q = f"?filter={filter_type}&task_id={st.task_id}"
            if list_id_int:
                q += f"&list_id={list_id_int}"
            if tag_id_int:
                q += f"&tag_id={tag_id_int}"
            if completed_filter:
                q += f"&completed={completed_filter}"
            if search_q:
                q += f"&q={search_q}"
            if sort_by != "date":
                q += f"&sort={sort_by}"
            return redirect(request.path + q)

    context = {
        "tasks": tasks,
        "lists": lists,
        "tags": tags,
        "lists_with_counts": lists_with_counts,
        "tags_with_counts": tags_with_counts,
        "filter_type": filter_type,
        "list_id": list_id_int,
        "tag_id": tag_id_int,
        "selected_task": selected_task,
        "today": today,
        "upcoming_count": upcoming_count,
        "today_count": today_count,
        "overdue_count": overdue_count,
        "total_tasks": total_tasks,
        "completed_count": completed_count,
        "pending_count": pending_count,
        "completed_filter": completed_filter or "",
        "search_q": search_q,
        "sort_by": sort_by,
    }
    return render(request, "todo.html", context)


@require_http_methods(["GET"])
def todo_task_detail_api(request, task_id):
    """GET: return task + subtasks as JSON."""
    task = get_object_or_404(
        Task.objects.prefetch_related("subtasks", "tags"), id=task_id
    )
    data = {
        "id": task.id,
        "title": task.title,
        "description": task.description or "",
        "due_date": task.due_date.isoformat() if task.due_date else None,
        "completed": task.completed,
        "priority": task.priority,
        "list_id": task.list_id,
        "list_name": task.list.name if task.list else None,
        "list_color": task.list.color if task.list else None,
        "tags": [
            {"id": t.id, "name": t.name, "color": t.color}
            for t in task.tags.all()
        ],
        "subtasks": [
            {"id": s.id, "title": s.title, "completed": s.completed}
            for s in task.subtasks.all()
        ],
    }
    return JsonResponse(data)


@login_required
@require_http_methods(["POST"])
def todo_toggle_api(request, task_id):
    """POST: toggle task completed status, return JSON. User-scoped."""
    task = get_object_or_404(Task, id=task_id, user=request.user)
    task.completed = not task.completed
    task.save()
    return JsonResponse({"completed": task.completed, "id": task.id})
