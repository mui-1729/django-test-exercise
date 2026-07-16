from django.shortcuts import render, redirect
from django.http import Http404
from django.utils.timezone import make_aware
from django.utils.dateparse import parse_datetime
from todo.models import Task

# Create your views here.


def _parse_due_at(value):
    if not value:
        return None

    due_at = parse_datetime(value)
    if due_at is None:
        return None
    return make_aware(due_at)


def _parse_priority(value):
    try:
        priority = int(value)
    except (TypeError, ValueError):
        return Task.PRIORITY_MEDIUM

    valid_priorities = {choice[0] for choice in Task.PRIORITY_CHOICES}
    return priority if priority in valid_priorities else Task.PRIORITY_MEDIUM


def index(request):
    if request.method == 'POST':
        task = Task(title=request.POST['title'],
                    due_at=_parse_due_at(request.POST.get('due_at')),
                    notes=request.POST.get('notes', ''),
                    priority=_parse_priority(request.POST.get('priority')))
        task.save()

    if request.GET.get('order') == 'priority':
        tasks = Task.objects.order_by('priority', '-posted_at')
    elif request.GET.get('order') == 'due':
        tasks = Task.objects.order_by('due_at')
    else:
        tasks = Task.objects.order_by('-posted_at')

    context = {
        'tasks': tasks,
        'priority_choices': Task.PRIORITY_CHOICES,
    }
    return render(request, 'todo/index.html', context)


def detail(request, task_id):
    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        raise Http404("Task does not exist")

    context = {
        'task': task,
    }
    return render(request, 'todo/detail.html', context)


def close(request, task_id):
    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        raise Http404("Task does not exist")

    task.mark_completed()
    return redirect('index')


def delete(request, task_id):
    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        raise Http404("Task does not exist")

    if request.method == 'POST':
        task.delete()
        return redirect('index')

    context = {
        'task': task,
    }
    return render(request, 'todo/delete_confirm.html', context)


def update(request, task_id):
    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        raise Http404('Task does not exist')
    if request.method == 'POST':
        task.title = request.POST['title']
        task.due_at = _parse_due_at(request.POST.get('due_at'))
        task.notes = request.POST.get('notes', '')
        task.priority = _parse_priority(request.POST.get('priority'))
        task.save()
        return redirect('detail', task_id=task.id)

    context = {
        'task': task,
        'priority_choices': Task.PRIORITY_CHOICES,
    }
    return render(request, 'todo/edit.html', context)
