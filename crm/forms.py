from django import forms
from .models import Project, Task, Communication, Invoice

class ProjectForm(forms.ModelForm):
	class Meta:
		model = Project
		fields = ['name', 'description', 'deadline', 'status']

		widgets = {
			'name': forms.TextInput(attrs={'class':'forms-control', 'placeholder': 'Введите название проекта'}),
			'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Введите описание'}),
			'deadline': forms.DateInput(attrs={'class':'form-control', 'type': 'date'}),
			'status': forms.Select(attrs={'class':'form-select'}),
		}

class TaskForm(forms.ModelForm):
	class Meta:
		model = Task
		fields = ['name', 'description', 'status']

		widgets = {
			'name': forms.TextInput(attrs={'class':'form-control', 'placeholder':'Введите название задачи'}),
			'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Введите описание задачи'}),
			'status': forms.Select(attrs={'class':'form-select'}),
		}

class CommunicationForm(forms.ModelForm):
    custom_tag = forms.CharField(required=False, label='Свой тег')
    
    class Meta:
        model = Communication 
        fields = ['message', 'tag', 'custom_tag', 'file']
        widgets = {
            'message': forms.Textarea(attrs={'rows':3, 'placeholder':'Вставьте важную информацию из переписки или добавьте свою заметку...'}),
            'tag': forms.Select(choices=Communication.TAG_CHOICES)
        }
		
class InvoiceForm(forms.ModelForm):
	class Meta:
		model = Invoice
		fields = ['salary_order', 'status_order']

		widgets = {
			'salary_order':forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
			'status_order':forms.Select(attrs={'class': 'form-select'}),
		}