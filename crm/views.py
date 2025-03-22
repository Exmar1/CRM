from django.shortcuts import render, get_object_or_404, redirect
from .forms import TaskForm, CommunicationForm, InvoiceForm, ProjectForm
from django.http import HttpResponse
from .models import Task, Message, Communication
from django.http import JsonResponse
from django.urls import reverse
from django.db.models import Q 
from django.utils.timezone import now, timedelta
from django.views.decorators.csrf import csrf_exempt
import json
# Create your views here.

def home(request):
	form = TaskForm()
	tasks = Task.objects.all()
	return render(request, 'crm/home.html', {'form': form, 'tasks':tasks})

def create_project(request):
		if request.method == 'POST':
			form = ProjectForm(request.POST)
			if form.is_valid():
				task = form.save()
				return render(request, 'crm/task_item.html', {'task':task})
		
			return JsonResponse({'error': 'Invalid form'}, status=400)

		return HttpResponse(status=400)

def create_task(request):
	if request.method == 'POST':
		form = TaskForm(request.POST)
		if form.is_valid():
			task = form.save()
			return render(request, 'crm/task_item.html', {'task':task})
	
		return JsonResponse({'error': 'Invalid form'}, status=400)
	
	return HttpResponse(status=400)

def delete_task(request, task_id):
	task = get_object_or_404(Task, id=task_id)
	
	if request.method == "POST":
			task.delete()
			return redirect('home')

	return render(request, 'crm/delete_confirmation.html', {'task': task})

def delete_communication(request, communication_id):
	communication = get_object_or_404(Communication, id=communication_id)

	if request.method == "POST":
			task_id = communication.task.id  
			communication.delete()
			return redirect(reverse('task_message', args=[task_id]))

	return render(request, 'crm/delete_communication.html', {'communication': communication})

def task_detail(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    context = {
        'task': task,
        'task_choices': Task.TASK_CHOICES
    }

    return render(request, 'crm/task_detail.html', context)

def update_task_status(request, task_id):
    """Простая вьюха для изменения статуса задачи"""
    if request.method == 'POST':
        task = get_object_or_404(Task, id=task_id)

        new_status = request.POST.get('status')

        if new_status in dict(Task.TASK_CHOICES):
            task.status = new_status
            task.save()
            return redirect('task_detail', task_id=task.id)

    return HttpResponse('Метод не разрешён', status=405)

def task_message(request, task_id):
    task = get_object_or_404(Task, id=task_id)

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
            communication.task = task  # Привязываем заметку к задаче
            if not communication.tag and form.cleaned_data['custom_tag']:
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

def add_communication(request, task_id):
	task = get_object_or_404(Task, id=task_id)

	if request.method == 'POST':
		form = CommunicationForm(request.POST, request.FILES)
		if form.is_valid():
			communication = form.save(commit=False)
			communication.task = task
			if not communication.tag:
				communication.tag = communication.custom_tag
			communication.save()
			return redirect('task_edit', task_id=task.id)
	else:
		form = CommunicationForm()

	return render(request, 'crm/add_communication.html', {'form':form, 'task':task})

def edit_message(request, message_id):
	message = get_object_or_404(Communication, id=message_id)

	if request.method == 'POST':
		form = CommunicationForm(request.POST, request.FILES, instance=message)
		if form.is_valid():
			form.save()
			return redirect('task_message', task_id=message.task.id)
		else:
			form = CommunicationForm(instance=message)
		return render(request, 'crm/edit_message.html', {
			'form': form,
			'message': message
    })
	
def edit_communication(request, communication_id):
	communication = get_object_or_404(Communication, id=communication_id)

	if request.method == 'POST':
			form = CommunicationForm(request.POST, request.FILES, instance=communication)
			if form.is_valid():
					form.save()
					return redirect('task_message', task_id=communication.task.id)
	else:
			form = CommunicationForm(instance=communication)

	return render(request, 'crm/edit_communication.html', {
			'form': form,
			'communication': communication
	})





