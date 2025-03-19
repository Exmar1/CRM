from django.shortcuts import render, get_object_or_404, redirect
from .forms import TaskForm, CommunicationForm, InvoiceForm, ProjectForm
from django.http import HttpResponse
from .models import Task, Message, Communication
from django.http import JsonResponse
from django.urls import reverse
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
	return render(request, 'crm/task_detail.html', {'task': task})

def task_message(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    communications = Communication.objects.filter(task=task).order_by('-created_at')

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

    return render(request, 'crm/task_message.html', {
        'task': task,
        'form': form,
        'communications': communications 
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





