from django.shortcuts import render, get_object_or_404, redirect
from .forms import TaskForm, CommunicationForm, InvoiceForm, ProjectForm
from django.http import HttpResponse
from .models import Task, Message, Communication
from django.http import JsonResponse
from django.urls import reverse
from django.db.models import Q 
from django.utils.timezone import now, timedelta
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .forms import RegistrationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
import json

@login_required
def home(request):
    tasks = Task.objects.filter(owner=request.user)
    form = TaskForm()
    return render(request, 'crm/home.html', {
        'tasks': tasks, 
        'form': form
    })

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = RegistrationForm()

    return render(request, 'crm/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, 'Вы успешно вошли в систему!')
            return redirect('home')
        else:
            messages.error(request, 'Неверный логин или пароль.')
    else:
        form = AuthenticationForm()
    
    return render(request, 'crm/login.html', {'form': form})

def user_logout(request):
    logout(request)
    messages.info(request, 'Вы вышли из системы.')
    return redirect(reverse('home')) 

@login_required
def create_task(request):
    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.owner = request.user
            task.save()
            
            # Проверяем, является ли запрос AJAX
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                # Возвращаем только шаблон элемента задачи без лишнего контекста
                return render(request, 'crm/task_item.html', {'task': task})
            # Если обычный запрос, перенаправляем на главную
            return redirect('home')
        else:
            # Если форма невалидна
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'errors': form.errors}, status=400)
            # Для обычного запроса выводим форму с ошибками
            return render(request, 'crm/home.html', {'form': form, 'tasks': Task.objects.filter(owner=request.user)})
    
    # Перенаправление на главную для GET-запросов
    return redirect('home')

@login_required
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, owner=request.user)
    
    if request.method == "POST" or request.method == "DELETE":  # Добавляем обработку DELETE
        task.delete()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success'})
        return redirect('home')

    return render(request, 'crm/delete_confirmation.html', {'task': task})

@login_required
def get_stats(request):
    user = request.user
    new_tasks = Task.objects.filter(owner=user, status='not_started').count()
    in_progress = Task.objects.filter(owner=user, status='in_progress').count()
    completed = Task.objects.filter(owner=user, status='completed').count()
    total = Task.objects.filter(owner=user).count()

    return JsonResponse({
        'new': new_tasks,
        'in_progress': in_progress,
        'completed': completed,
        'total': total
    })

@login_required
def task_detail(request, task_id):
    task = get_object_or_404(Task, id=task_id, owner=request.user)
    
    recent_notes = Communication.objects.filter(task=task).order_by('-created_at')
    
    current_time = now()

    return render(request, 'crm/task_detail.html', {
        'task': task, 
        'recent_notes': recent_notes,
        'now': current_time
    })

@login_required
def edit_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, owner=request.user)

    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('task_detail', task_id=task.id)

    else:
        form = TaskForm(instance=task)

    return render(request, 'crm/edit_task.html', {'form': form, 'task': task})

@login_required
def create_project(request):
    if request.method == 'POST':    
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            return redirect('project_list')  # или другая нужная вьюха
    else:
        form = ProjectForm()

    return render(request, 'crm/create_project.html', {'form': form})

@login_required
def update_task_status(request, task_id):
    if request.method == 'POST':
        task = get_object_or_404(Task, id=task_id, owner=request.user)

        new_status = request.POST.get('status')

        if new_status in dict(Task.TASK_CHOICES):
            task.status = new_status
            task.save()
            return redirect('task_detail', task_id=task.id)

    return HttpResponse('Метод не разрешён', status=405)

@login_required
def task_message(request, task_id):
    task = get_object_or_404(Task, id=task_id, owner=request.user)

    query = request.GET.get('q', '')
    date_filter = request.GET.get('date_filter', '')
    tag_filter = request.GET.get('tag_filter', '')
    has_file = request.GET.get('has_file', '')

    communications = Communication.objects.filter(task=task).order_by('-created_at')

    if query:
        communications = communications.filter(
            Q(message__icontains=query) |
            Q(tag__icontains=query)
        )

    if date_filter == 'today':
        communications = communications.filter(created_at__date=now().date())
    elif date_filter == 'week':
        week_ago = now() - timedelta(days=7)
        communications = communications.filter(created_at__gte=week_ago)
    elif date_filter == 'month':
        month_ago = now() - timedelta(days=30)
        communications = communications.filter(created_at__gte=month_ago)
    
    if tag_filter:
        communications = communications.filter(tag=tag_filter)

    if has_file == 'yes':
        communications = communications.filter(file__isnull=False)
    elif has_file == 'no':
        communications = communications.filter(file__isnull=True)
    
    if request.method == 'POST':
        form = CommunicationForm(request.POST, request.FILES)
        if form.is_valid():
            communication = form.save(commit=False)
            communication.task = task
            if not communication.tag and form.cleaned_data.get('custom_tag'):
                communication.tag = form.cleaned_data['custom_tag']
            communication.save()
            return redirect('task_message', task_id=task.id)
    else:
        form = CommunicationForm()

    tags = Communication.objects.filter(task=task).values_list('tag', flat=True).distinct()

    return render(request, 'crm/task_message.html', {
        'task': task,
        'form': form,
        'communications': communications,
        'query': query,
        'date_filter': date_filter,
        'tag_filter': tag_filter,
        'has_file': has_file,
        'tags': tags, 
    })

@login_required
def add_communication(request, task_id):
    task = get_object_or_404(Task, id=task_id, owner=request.user)

    if request.method == 'POST':
        form = CommunicationForm(request.POST, request.FILES)
        if form.is_valid():
            communication = form.save(commit=False)
            communication.task = task
            if not communication.tag:
                communication.tag = form.cleaned_data.get('custom_tag', '')
            communication.save()
            return redirect('task_message', task_id=task.id)
    else:
        form = CommunicationForm()

    return render(request, 'crm/add_communication.html', {'form': form, 'task': task})

@login_required
def edit_communication(request, communication_id):
    communication = get_object_or_404(Communication, id=communication_id)
    task = communication.task
    
    # Проверяем, что задача принадлежит текущему пользователю
    if task.owner != request.user:
        return HttpResponseForbidden("Вы не имеете доступа к этой задаче!")

    if request.method == 'POST':
        form = CommunicationForm(request.POST, request.FILES, instance=communication)
        if form.is_valid():
            form.save()
            return redirect('task_message', task_id=task.id)
    else:
        form = CommunicationForm(instance=communication)

    return render(request, 'crm/edit_communication.html', {
        'form': form,
        'communication': communication
    })

@login_required
def delete_communication(request, communication_id):
    communication = get_object_or_404(Communication, id=communication_id)
    task = communication.task
    
    # Проверяем, что задача принадлежит текущему пользователю
    if task.owner != request.user:
        return HttpResponseForbidden("Вы не имеете доступа к этой задаче!")

    if request.method == "POST":
        task_id = task.id
        communication.delete()
        return redirect(reverse('task_message', args=[task_id]))

    return render(request, 'crm/delete_communication.html', {'communication': communication})