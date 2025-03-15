from django.shortcuts import render, get_object_or_404
from .forms import TaskForm, CommunicationForm, InvoiceForm, ProjectForm
from django.http import HttpResponse
from .models import Task
from django.http import JsonResponse
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
    task.delete()  
    return JsonResponse({'message': 'Задача удалена'}, status=200)

def task_detail(request, task_id):
	task = get_object_or_404(Task, id=task_id)
	data = {
		"id": task.id,
		"name": task.name,
		"description": task.description,
		"status": task.get_status_display(),
    }
	return JsonResponse(data)



