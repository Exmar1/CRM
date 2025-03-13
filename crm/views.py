from django.shortcuts import render
from .forms import TaskForm, CommunicationForm, InvoiceForm, ProjectForm
from django.http import HttpResponse
from .models import Task
# Create your views here.

def home(request):
	form = TaskForm()
	tasks = Task.objects.all()
	return render(request, 'crm/home.html', {'form': form, 'tasks':tasks})

def create_project(request):
		if request.method == 'POST':
			form = ProjectForm(request.POST)
			task = None

			if form.is_valid():
				task = form.save()
			return render(request, 'crm/task_item.html', {'task':task})

		return HttpResponse(status=400)

def create_task(request):
	if request.method == 'POST':
		form = TaskForm(request.POST)
		task = None

		if form.is_valid():
			task = form.save()
		return render(request, 'crm/task_item.html', {'task':task})
	
	return HttpResponse(status=400)

